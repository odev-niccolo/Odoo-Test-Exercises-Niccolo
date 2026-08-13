Exercise 3

FUNCTIONAL REQUIREMENTS
- When converting a Lead to Opportunity, a corresponding Project is to be created and linked to newly converted Opportunity
- User will have the option to automatically create a corresponding Project or create it manually

OUT OF SCOPE:
	- Content of newly created Project 
	- Deadline of Project
	- Duplicate Opportunities which might cause the newly created project to be linked to the wrong opportunity

Test Cases:

ETE 1_1: Lead Creation
	Description: Verify if Lead is created successfully.
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

ETE 1_2: Convert to Opportunity Behavior
	Description: Verify if a project is created automatically when Lead is converted to Opportunity.
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





	