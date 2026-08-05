Functional Specifications
* Allows employees to submit improvement suggestions 
* Up-vote ideas submitted by colleagues. 
* Managers can review, approve, or reject suggestions. 

Critical business rules that require verification
* Only employees with a bound HR employee profile can cast give upvotes
* Employees cannot upvote their own suggestions
* An employee can only upvote a specific suggestion once
* Suggestions can only be upvoted when in “Ready for Upvote” State

Restrictions
* Suggestions cannot be reverted to “Draft” if one or more upvotes were received
* A suggestion status can only be moved to “Approved” or “Rejected” if already in “Ready for Upvote” status.

Authorization
* Only users with “Suggestion Approver” role can approve or reject suggestions.

UNIT TESTS
Test Case 1: Standard Workflow
Test Case 1.1: Create Suggestion
OBJECTIVE: VERIFY END-TO-END APPROVAL PROCESS FOR A NEW SUGGESTION
	Normal Employee
1. Log in as normal Employee
2. Navigate to:
    1. Suggestion Box App 
    2. My Suggestions
    3. Click “New”
3. Enter Title and Description, then save.
EXPECTED RESULT: Suggestion is Saved; State is ‘Draft’
Test Case 1.2: Confirm Suggestion
1. Log in as normal Employee
2. Navigate to:
    1. Suggestion Box App 
    2. My Suggestions
    3. Click existing Suggestion with ‘Draft’ Status
    4. Click “Confirm” button
EXPECTED RESULT: Suggestion is Saved; State is moved to “Ready for Upvote”
Test Case 1.3: Approve Suggestion
1. Log in as Suggestion Approver
2. Navigate to
    1. Suggestion Box
    2. To Upvote
3. Open Suggestion then click “Approve”
EXPECTED RESULT: Suggestion State is moved to “Approve”

Test Case 1.4: Reject Suggestion
1. Log in as Suggestion Approver
2. Navigate to
    1. Suggestion Box
    2. To Upvote
3. Open Suggestion then click “Reject”
EXPECTED RESULT: Suggestion State is moved to “Rejected”

Test Case 2: Invalid State Approval
1. Log in as an Employee, create a suggestion, and leave it in the Draft state.
2. Log out and log in as a Suggestion Approver.
3. Open the draft suggestion. 
Expected Result: The Suggestion in Draft State is not visible

Test Case 3: Upvote Constraints
Test Case 3.1: Upvote as Suggestion Author
1. Log in as Normal Employee and create a suggestion. 
2. Click "Confirm". Attempt to click "Upvote" as the Author.
Expected Result: The Upvote Button is not visible
Test Case 3.2: Upvote Only Once

1. Log in as a second Employee (Voter). Open the suggestion and click "Upvote".
2. Attempt to click "Upvote" a second time as the Voter. Expected Result: A Validation Error appears saying current user has already upvoted this suggestions



