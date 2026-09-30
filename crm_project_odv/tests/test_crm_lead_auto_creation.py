from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase


@tagged("post_install", "-at_install", "test_crm_project_odv")
class TestProjectAutoCreationFromLead(SingleTransactionCase):
    
    ######################
    # Setup              #
    ######################
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        sales_admin_group = cls.env.ref("sales_team.group_sale_manager")
        project_admin_group = cls.env.ref("project.group_project_manager")

        cls.sales_admin = cls.env["res.users"].create({
            "name": "E2E Test User",
            "login": "e2e_test_user",
            "group_ids": [(6, 0, [sales_admin_group.id, project_admin_group.id])]
        })
        cls.customer = cls.env["res.partner"].create({
            "name": "Azure Interior"
        })
    
    ######################
    # Unit Tests         #
    ######################

    ######################
    # E2E Tests          #
    ###################### 
    def test_ete1_1_lead_creation(self):
        """
        ETE1-1: Lead Creation
        Steps: 
            1. Go to CRM > Leads 
            2. Click New, 
            3. Type in:
                Name: "Office Renovation", 
                (Customer on UAT)Contact: "Azure Interior", 
            4. Click Save
        EXPECTED BEHAVIOR:
        Lead is created with type 'lead'.
        """
        self.lead = (
            self.env["crm.lead"]
            .with_user(self.sales_admin)
            .with_context(mail_create_nolog=True, mail_notrack=True)
            .create(
                {
                    "name": "Office Renovation",
                    "partner_id": self.customer.id,
                    "type": "lead",
                }
            )
        )
        
        self.assertTrue(self.lead.id, "Lead should be created successfully.")
        self.assertEqual(self.lead.type, "lead", "The created record type should be 'lead'.")

    def test_ete1_2_convert_to_opportunity_with_project(self):
        """
        ETE1-2: 
        TEST CASE: Convert to Opportunity with Project
        Steps: 
            1. Open Lead from ETE1-1, 
            2. Click Convert to Opportunity, 
            3. Select "Create Project"
            4. Click Create Opportunity
        EXPECTED BEHAVIOR: 
            1. Lead is converted to Opportunity.
            2. A new Project named "Office Renovation" is created.
            3. The Project is linked to the Opportunity.
        """

        # Search by both name and the specific customer to guarantee the correct lead
        lead = self.env["crm.lead"].search([
            ("name", "=", "Office Renovation"),
            ("partner_id", "=", self.customer.id)
        ], limit=1)

        wizard = self.env["crm.lead2opportunity.partner"].with_user(self.sales_admin).with_context(
            active_model="crm.lead",
            active_id=lead.id,
            active_ids=lead.ids
        ).create({
            "name": "convert",
            "lead_id": lead.id,
            "create_project": True, 
        })
        wizard.action_apply()

        # Expected Behavior 1
        self.assertEqual(lead.type, "opportunity", "Lead type should be 'opportunity'.")


        project = self.env["project.project"].search([
            ("name", "=", "Office Renovation"),
            ("partner_id", "=", self.customer.id)
        ])
        # Expected Behavior 2
        self.assertTrue(project, "New Project 'Office Renovation' should be automatically created.")

        # Expected Behavior 3
        self.assertEqual(lead.project_id.id, project.id, "New Project should be linked to the Opportunity.")

    def test_ete1_3_convert_to_opportunity_without_project(self):
        """
        ETE1-3: 
        TEST CASE: Convert to Opportunity without Project
        Steps: 
            1. Create a new lead named "Store Expansion"
            2. Click Convert to Opportunity, 
            3. Ensure "Create Project" is UNSELECTED
            4. Click Create Opportunity
        EXPECTED BEHAVIOR: 
            1. Lead is converted to Opportunity.
            2. No project is linked to the Opportunity.
        """

        # 1. Create a new lead different from ETE 1-2
        lead_no_project = self.env["crm.lead"].with_user(self.sales_admin).with_context(
            mail_create_nolog=True,
            mail_notrack=True
        ).create({
            "name": "Store Expansion",
            "partner_id": self.customer.id,
            "type": "lead",
        })

        # 2. Run the wizard
        wizard = self.env["crm.lead2opportunity.partner"].with_user(self.sales_admin).with_context(
            active_model="crm.lead",
            active_id=lead_no_project.id,
            active_ids=lead_no_project.ids
        ).create({
            "name": "convert",
            "lead_id": lead_no_project.id,
            "create_project": False,
        })
        wizard.action_apply()

        # Expected Behavior 1: Lead is converted
        self.assertEqual(lead_no_project.type, "opportunity",
                         "Lead type should be 'opportunity'.")

        # Expected Behavior 2: Ensure the project_id field is empty
        self.assertFalse(lead_no_project.project_id,
                         "No project should be linked to this Opportunity.")

    def test_ete1_4_duplicate_conversion_with_project(self):
        """
        ETE1-4: Duplicate/Repeated Conversion With Project
        TEST CASE: Attempt to convert a lead that has already been converted.
        Steps: 
            1. Fetch converted opportunity "Office Renovation"
            2. Run the conversion wizard a second time on the same record (create_project=True).
        EXPECTED BEHAVIOR: 
            1. The lead is not found
            2. Odoo does NOT create a second duplicate project.
            3. The lead remains linked to the original project.
        """

        # 1. Fetch the already converted opportunity from ETE1-2
        lead = self.env["crm.lead"].search([
            ("name", "=", "Office Renovation"),
            ("partner_id", "=", self.customer.id)
        ], limit=1)

        # Verify if correct opportunity is fetched
        self.assertEqual(lead.type, "opportunity",
                         "Prerequisite: Lead should already be an opportunity.")
        first_project_id = lead.project_id.id
        self.assertTrue(
            first_project_id, "Prerequisite: Project should already exist from ETE1-2.")

        # 2. Try to convert for a second time
        wizard2 = self.env["crm.lead2opportunity.partner"].with_user(self.sales_admin).with_context(
            active_model="crm.lead",
            active_id=lead.id,
            active_ids=lead.ids
        ).create({
            "name": "convert",
            "lead_id": lead.id,
            "create_project": True,
        })
        wizard2.action_apply()

        # 3. Check for projects named "Office Renovation"
        all_projects = self.env["project.project"].search([
            ("name", "=", "Office Renovation"),
            ("partner_id", "=", self.customer.id)
        ])

        # Assert that only one project exists for this specific workflow
        self.assertEqual(len(
            all_projects), 1, "Odoo should prevent creating a duplicate project on repeated conversion.")

        # Assert the lead is still linked to the original project
        self.assertEqual(lead.project_id.id, first_project_id,
                         "The original project link should remain unchanged.")

    def test_ete1_5_duplicate_conversion_without_project(self):
        """
        ETE1-5: Duplicate/Repeated Conversion Without Project
        TEST CASE: Attempt to convert a lead that has already been converted, 
                   keeping "Create Project" unselected.
        Steps: 
            1. Fetch the already converted opportunity "Store Expansion".
            2. Run the conversion wizard a second time on the same record (create_project=False).
        EXPECTED BEHAVIOR: 
            1. Lead remains an opportunity.
            2. No project is ever created in the database.
            3. The opportunity's project_id field remains empty.
        """

        # 1. Fetch the already converted opportunity from ETE1-3
        lead_no_project = self.env["crm.lead"].search([
            ("name", "=", "Store Expansion"),
            ("partner_id", "=", self.customer.id)
        ], limit=1)

        # Ensure correct lead is fetched
        self.assertEqual(lead_no_project.type, "opportunity",
                         "Prerequisite: Lead should already be an opportunity.")
        self.assertFalse(lead_no_project.project_id,
                         "Prerequisite: Project should NOT exist from ETE1-3.")

        # 2. Second Conversion Attempt
        wizard2 = self.env["crm.lead2opportunity.partner"].with_user(self.sales_admin).with_context(
            active_model="crm.lead",
            active_id=lead_no_project.id,
            active_ids=lead_no_project.ids
        ).create({
            "name": "convert",
            "lead_id": lead_no_project.id,
            "create_project": False,
        })
        wizard2.action_apply()

        # 3. Check database for existing projects named "Store Expansion"
        all_projects = self.env["project.project"].search([
            ("name", "=", "Store Expansion"),
            ("partner_id", "=", self.customer.id)
        ])

        # Assert that no project is created
        self.assertEqual(len(
            all_projects), 0, "System must not create a project when create_project is False on repeated conversion.")

        # Assert the opportunity is not linked to any projects as well
        self.assertFalse(lead_no_project.project_id,
                         "The opportunity should still not be linked to any project.")
