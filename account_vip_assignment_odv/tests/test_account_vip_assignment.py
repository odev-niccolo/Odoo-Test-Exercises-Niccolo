# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, new_test_user, tagged
from odoo import Command

@tagged("test_account_vip_assignment", "-at_install", "post_install")
class TestAccountVipAssignment(TransactionCase):

    ######################
    # Setup              #
    ######################
    @classmethod
    def setUpClass(cls):
        super(TestAccountVipAssignment, cls).setUpClass()
        cls.accounting_user = new_test_user(cls.env, 
                                            login="accounting",
                                            groups="account.group_account_manager")
        cls.company = cls.env.ref("base.main_company")
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Partner",
        })
        
        cls.company.write({"vip_threshold": 50000.0})

        
        cls.company_vip_10000 = cls.env.ref("base.main_company")
        cls.company_vip_10000.write({"vip_threshold": 10000.0})
        
        
        cls.company_vip_20000 = cls.env["res.company"].create({
            "name": "Company VIP 20000",
            "vip_threshold": 20000.0,
        })
        
        cls.company_vip_50000 = cls.env["res.company"].create({
            "name": "Company VIP 50000",
            "vip_threshold": 50000.0,
        })
        
    ######################
    # Unit Tests         #
    ######################
    def test_is_vip_computation(self):
        invoice = self._create_invoice(self.partner, 10000.0)
        invoice.action_post()
        self.assertTrue(self.partner.is_vip)
    
    def test_is_not_vip_computation(self):
        invoice = self._create_invoice(self.partner, 5000.0)
        invoice.action_post()
        self.assertFalse(self.partner.is_vip)
    
    def test_posted_invoice_counts_toward_vip(self):
        partner = self._create_partner("Customer Posted Invoice", self.company_vip_10000)
        invoice = self._create_invoice(partner, 12000.0)
        invoice.action_post()
        self.assertTrue(partner.is_vip)
    
    def test_canceled_invoice_excluded_from_vip(self):
        partner = self._create_partner("Customer Canceled Invoice", self.company_vip_10000)
        invoice = self._create_invoice(partner, 15000.0)
        invoice.button_cancel()
        self.assertFalse(partner.is_vip)
    
    def test_draft_invoice_excluded_from_vip(self):
        partner = self._create_partner("Customer Draft Invoice", self.company_vip_10000)
        invoice = self._create_invoice(partner, 15000.0)
        self.assertFalse(partner.is_vip)
 
    def test_multiple_posted_invoices_sum_correctly(self):
        partner = self._create_partner("Customer Multiple Sum Correctly", self.company_vip_10000)
        invoice1 = self._create_invoice(partner, 3000.0)
        invoice1.action_post()
        invoice2 = self._create_invoice(partner, 4000.0)
        invoice2.action_post()
        invoice3 = self._create_invoice(partner, 5000.0)
        invoice3.action_post()
        self.assertTrue(partner.is_vip)
    
    def test_multiple_posted_invoices_below_threshold(self):
        partner = self._create_partner("Customer Multiple Below Threshold", self.company_vip_10000)
        invoice1 = self._create_invoice(partner, 2000.0)
        invoice1.action_post()
        invoice2 = self._create_invoice(partner, 3000.0)
        invoice2.action_post()
        invoice3 = self._create_invoice(partner, 4000.0)
        invoice3.action_post()
        self.assertFalse(partner.is_vip)
    
    def test_default_threshold_when_no_company(self):
        partner = self._create_partner("Customer No Company Default", None)
        invoice = self._create_invoice(partner, 10000.0)
        invoice.action_post()
        self.assertTrue(partner.is_vip)
 
    def test_default_threshold_when_no_company_not_vip(self):
        partner = self._create_partner("Customer No Company Default Not VIP", None)
        invoice = self._create_invoice(partner, 5000.0)
        invoice.action_post()
        self.assertFalse(partner.is_vip)
    
    def test_company_specific_threshold_overwrite_default(self):
        partner = self._create_partner("Customer Company Specific", self.company_vip_10000)
        self.company_vip_10000.write({"vip_threshold": 50000.0})
        invoice = self._create_invoice(partner, 45000.0)
        invoice.action_post()
        self.assertFalse(partner.is_vip)
    
    def test_changing_threshold_affects_existing_customers(self):
        partner = self._create_partner("Customer Dynamic Threshold", self.company_vip_10000)
        invoice = self._create_invoice(partner, 12000.0)
        invoice.action_post()
        self.assertTrue(partner.is_vip)
        
        self.company_vip_10000.write({"vip_threshold": 15000.0})
        partner.invalidate_recordset()
        self.assertFalse(partner.is_vip)
        
        self.company_vip_10000.write({"vip_threshold": 10000.0})
        partner.invalidate_recordset()
        self.assertTrue(partner.is_vip)
    
    def test_only_partners_company_invoices_counted(self):
        partner = self._create_partner("Customer Same Company Only", self.company_vip_10000)
        invoice1 = self._create_invoice(partner, 8000.0)
        invoice1.action_post()
        self.assertFalse(partner.is_vip)
        
        partner.invalidate_recordset()

        invoice2 = self._create_invoice(partner, 3000.0)
        invoice2.action_post()
        partner.invalidate_recordset()
        self.assertTrue(partner.is_vip)


    ######################
    # Helper Methods     #
    ######################

    def _create_partner(self, name, company=None):
        partner = self.env["res.partner"].create({
            "name": name,
            "company_id": company.id if company else False,
        })
        return partner
    
    def _create_invoice(self, partner, amount):
        invoice = self.env["account.move"].with_user(self.accounting_user).create({
            "partner_id": partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids" : [Command.create({
                "name": "Test Invoice Line",
                "quantity": 1,
                "price_unit": amount,
            })],
        })
        return invoice
        