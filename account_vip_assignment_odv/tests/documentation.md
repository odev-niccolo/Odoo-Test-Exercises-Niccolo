Exercise 2

Functional Requirements
- Companies can now qualify for VIP status, which is based on their assigned quota/threshold
- Company is automatically marked as VIP if total sum of their completed sales meets VIP Threshold
- VIP Threshold for each company can be customized.
- Customer VIP Status shall be displayed as a ribbon, if not VIP, no ribbon will appear
- Default Threshold is 10000

OUT OF SCOPE
- No additional features have been determined for VIP Companies
[NOTES]
- Customer pertains to res.partner
- Company is res.company (will be linked to res.partner)
Issues
- Cancelled transactions contribute to the calculation of VIP Threshold (possibly no filter for successful state only)
- Customized VIP Threshold not reflecting
Cause of Issue in Code
	No Filter in this block:
    domain = [
            ("move_type", "=", "out_invoice"),
            ("partner_id", "=", partner.id),]
Approach
	Add line for filtering
    ("state", "=", "posted") to domain

1. VIP Computation (Single Invoice = Threshold)
Description: Verify if a single invoice with amount equal to threshold triggers VIP status
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Test Partner
4. Set Journal to Sales
5. Insert Invoice line with amount: 10000
6. Click "Confirm" button
7. Navigate to: Contacts > Test Partner
EXPECTED RESULT: VIP Ribbon is visible, vip_field is TRUE

2. NOT VIP Computation (Below Threshold)
Description: Verify if a single invoice below threshold does NOT trigger VIP status
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Test Partner
4. Set Journal to Sales
5. Insert Invoice line with amount: 5000
6. Click "Confirm" button
7. Navigate to: Contacts > Test Partner
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE


3. Posted Invoice Counts Toward VIP
Description: Verify if only posted invoices are counted in tallies for VIP calculation
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer Posted Invoice
4. Set Journal to Sales
5. Insert Invoice line with amount: 12000
6. Click "Confirm" button
7. Navigate to: Contacts > Customer Posted Invoice
EXPECTED RESULT: VIP Ribbon is visible, vip_field is TRUE


4. Canceled Invoice Not Counted in VIP Calculation
Description: Verify if cancelled invoices are excluded from VIP Calculation
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer Canceled Invoice
4. Set Journal to Sales
5. Insert Invoice line with amount: 15000
6. Click "Confirm" button
7. Click "Cancel" button to cancel the invoice
8. Navigate to: Contacts > Customer Canceled Invoice
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE


5. Draft Invoice Not Counted in VIP Calculation
Description: Verify if invoices in DRAFT state are excluded from VIP Calculation
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer Draft Invoice
4. Set Journal to Sales
5. Insert Invoice line with amount: 15000
6. Click "Save" button (DO NOT confirm - keep in DRAFT)
7. Navigate to: Contacts > Customer Draft Invoice
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE


6. Multiple Posted Invoices Sum Correctly
Description: Verify if multiple posted invoices are summed correctly for VIP calculation (3000 + 4000 + 5000 = 12000 >= 10000)
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create 1st invoice
3. Select Customer: Customer Multiple Sum Correctly
4. Set Journal to Sales
5. Insert Invoice line with amount: 3000
6. Click "Confirm" button
7. Repeat steps 1-6, inputting amount to 4000
8. Repeat steps 1-6, inputting amount to 5000
9. Navigate to: Contacts > Customer Multiple Sum Correctly
EXPECTED RESULT: VIP Ribbon is visible, vip_field is TRUE


7. Multiple Posted Invoices Below Threshold
Description: Verify if multiple posted invoices that sum below threshold do NOT trigger VIP status (2000 + 3000 + 4000 = 9000 < 10000)
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create 1st invoice
3. Select Customer: Customer Multiple Below Threshold
4. Set Journal to Sales
5. Insert Invoice line with amount: 2000
6. Click "Confirm" button
7. Repeat steps 1-6, inputting amount to 3000
8. Repeat steps 1-6, inputting amount to 4000
9. Navigate to: Contacts > Customer Multiple Below Threshold
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE


8. Default Threshold When No Company Assigned (VIP)
Description: Verify if default threshold (10000) is used when partner has no company assigned
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer No Company Default
4. Set Journal to Sales
5. Insert Invoice line with amount: 10000
6. Click "Confirm" button
7. Navigate to: Contacts > Customer No Company Default
8. Verify Company field is empty
EXPECTED RESULT: VIP Ribbon is visible, vip_field is TRUE (Default threshold 10000 applied)


9. Default Threshold - Below Threshold (No Company)
Description: Verify if default threshold prevents VIP status when amount is below threshold and no company assigned
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer No Company Default Not VIP
4. Set Journal to Sales
5. Insert Invoice line with amount: 5000
6. Click "Confirm" button
7. Navigate to: Contacts > Customer No Company Default Not VIP
8. Verify Company field is empty
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE (Default threshold 10000 applied)


10. Company-Specific Threshold Overrides Default
Description: Verify if company-specific threshold overrides the default threshold
1. Navigate to Settings > Companies
2. Select Company VIP 10000
3. Change VIP Threshold to 50000
4. Click "Save" button
5. Navigate to Invoicing > Customers > Invoices
6. Click "New" to create invoice
7. Select Customer: Customer Company Specific
8. Set Journal to Sales
9. Insert Invoice line with amount: 45000
10. Click "Confirm" button
11. Navigate to: Contacts > Customer Company Specific
EXPECTED RESULT: VIP Ribbon is NOT visible, vip_field is FALSE (45000 < 50000 company threshold)


11. Changing Threshold Affects Existing Customers
Description: Verify if changing company threshold dynamically affects VIP status of existing customers
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create invoice
3. Select Customer: Customer Dynamic Threshold
4. Set Journal to Sales
5. Insert Invoice line with amount: 12000
6. Click "Confirm" button
7. Navigate to: Contacts > Customer Dynamic Threshold
8. Verify VIP Ribbon is visible (12000 >= 10000)
9. Navigate to Settings > Companies
10. Select Company VIP 10000
11. Change VIP Threshold to 15000
12. Click "Save" button
13. Navigate back to: Contacts > Customer Dynamic Threshold
14. Refresh the page
15. Verify VIP Ribbon is NOT visible (12000 < 15000)
16. Navigate to Settings > Companies
17. Select Company VIP 10000
18. Change VIP Threshold back to 10000
19. Click "Save" button
20. Navigate back to: Contacts > Customer Dynamic Threshold
21. Refresh the page
EXPECTED RESULT: VIP status changes dynamically - Initially TRUE (12000 >= 10000), becomes FALSE when threshold is 15000, becomes TRUE again when threshold is reset to 10000


12. Only Partner's Company Invoices Counted
Description: Verify if only invoices from the partner's assigned company are counted toward VIP calculation
1. Navigate to Invoicing > Customers > Invoices
2. Click "New" to create 1st invoice
3. Select Customer: Customer Same Company Only
4. Set Journal to Sales
5. Insert Invoice line with amount: 8000
6. Click "Confirm" button
7. Navigate to: Contacts > Customer Same Company Only
8. Verify VIP Ribbon is NOT visible (8000 < 10000)
9. Navigate back to Invoicing > Customers > Invoices
10. Click "New" to create 2nd invoice
11. Select Customer: Customer Same Company Only
12. Set Journal to Sales
13. Insert Invoice line with amount: 3000
14. Click "Confirm" button
15. Navigate to: Contacts > Customer Same Company Only
16. Refresh the page
EXPECTED RESULT: After 1st invoice (8000): VIP Ribbon NOT visible. After 2nd invoice (3000): VIP Ribbon visible (8000 + 3000 = 11000 >= 10000)





