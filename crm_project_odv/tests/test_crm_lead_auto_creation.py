from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase

@tagged("post_install", "-at_install", "test_project_auto_creation")
class TestProjectAutoCreation(SingleTransactionCase):
    
    ######################
    # Setup              #
    ######################
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        sales_group = cls.env.ref("sales_team.group_sale_salesman")
        project_admin_group = cls.env.ref("project.group_project_manager")

        cls.salesperson = cls.env["res.users"].create({
            "name": "E2E Test User",
            "login": "e2e_test_user",
            "group_ids": [(6, 0, [sales_group.id, project_admin_group.id])]
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
            .with_user(self.salesperson)
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

    def test_ete1_2_convert_to_opportunity(self):
        """
        ETE1-2: 
        TEST CASE: Convert to Opportunity
        Steps: 
            1. Open Lead from ETE1-1, 
            2. Click Convert to Opportunity, 
            3. Select "Convert to Opportunity"
            4. Click Create Opportunity
        EXPECTED BEHAVIOR: 
            1. Lead is converted to Opportunity.
            2. A new Project named "Office Renovation" is created.
            3. The Project is linked to the Opportunity.
        """

        # FIX 1: Search by both name and the specific customer to guarantee the correct lead
        lead = self.env["crm.lead"].search([
            ("name", "=", "Office Renovation"),
            ("partner_id", "=", self.customer.id)
        ], limit=1)

        wizard = self.env["crm.lead2opportunity.partner"].with_user(self.salesperson).with_context(
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