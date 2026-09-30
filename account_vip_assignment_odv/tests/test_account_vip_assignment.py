# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, new_test_user, tagged, Form
from odoo.exceptions import ValidationError, AccessError
from odoo import Command


@tagged("test_account_vip_assignment_odv", "-at_install", "post_install")
class TestAccountVipAssignmentOdv(TransactionCase):

    ######################
    # Setup              #
    ######################
    @classmethod
    def setUpClass(cls):
        super(TestAccountVipAssignmentOdv, cls).setUpClass()

        # Users
        cls.accounting_user = new_test_user(cls.env, 
                                            login="accounting",
                                            groups="account.group_account_manager")

        cls.non_accounting_user = new_test_user(cls.env,
                                                login="basic",
                                                groups="base.group_user")

        # Companies
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

        # Find(Demo)/Create(Blank) account journal
        def _create_journal(company):
            journal = cls.env["account.journal"].search([
                ("type", "=", "sale"),
                ("company_id", "=", company.id)
            ], limit=1)

            if not journal:
                journal = cls.env["account.journal"].create({
                    "name": f"Test Sales Journal {company.id}",
                    "code": f"SLS{company.id}",
                    "type": "sale",
                    "company_id": company.id,
                })
            return journal
        # Find(Demo)/Create(Blank) bank journal

        def _create_bank_journal(company):
            journal = cls.env["account.journal"].search([
                ("type", "=", "bank"),
                ("company_id", "=", company.id)
            ], limit=1)

            if not journal:
                journal = cls.env["account.journal"].create({
                    "name": f"Test Bank Journal {company.id}",
                    "code": f"BNK{company.id}",
                    "type": "bank",
                    "company_id": company.id,
                })
            return journal

        _create_journal(cls.company)
        _create_bank_journal(cls.company)

        _create_journal(cls.company_vip_20000)
        _create_bank_journal(cls.company_vip_20000)

        _create_journal(cls.company_vip_50000)
        _create_bank_journal(cls.company_vip_50000)


    ######################
    # Unit Tests         #
    ######################
    def test_is_vip_computation(self):
        invoice = self._create_invoice(self.partner, 10000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertTrue(self.partner.is_vip)
    
    def test_is_not_vip_computation(self):
        invoice = self._create_invoice(self.partner, 5000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertFalse(self.partner.is_vip)

    def test_posted_invoice_counts_toward_vip(self):
        partner = self._create_partner("Customer Posted Invoice", self.company_vip_10000)
        invoice = self._create_invoice(partner, 12000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertTrue(partner.is_vip)

    def test_canceled_invoice_excluded_from_vip(self):
        partner = self._create_partner("Customer Canceled Invoice", self.company_vip_10000)
        invoice = self._create_invoice(partner, 15000.0)
        invoice.action_post()
        self.assertTrue(partner.is_vip)

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
        self._pay_invoice(invoice1)

        invoice2 = self._create_invoice(partner, 4000.0)
        invoice2.action_post()
        self._pay_invoice(invoice2)

        invoice3 = self._create_invoice(partner, 5000.0)
        invoice3.action_post()
        self._pay_invoice(invoice3)

        self.assertTrue(partner.is_vip)

    def test_multiple_posted_invoices_below_threshold(self):
        partner = self._create_partner("Customer Multiple Below Threshold", self.company_vip_10000)
        invoice1 = self._create_invoice(partner, 2000.0)
        invoice1.action_post()
        self._pay_invoice(invoice1)

        invoice2 = self._create_invoice(partner, 3000.0)
        invoice2.action_post()
        self._pay_invoice(invoice2)

        invoice3 = self._create_invoice(partner, 4000.0)
        invoice3.action_post()
        self._pay_invoice(invoice3)
        self.assertFalse(partner.is_vip)

    def test_default_threshold_when_no_company(self):
        partner = self._create_partner("Customer No Company Default", None)
        invoice = self._create_invoice(partner, 10000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertTrue(partner.is_vip)

    def test_default_threshold_when_no_company_not_vip(self):
        partner = self._create_partner("Customer No Company Default Not VIP", None)
        invoice = self._create_invoice(partner, 5000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertFalse(partner.is_vip)

    def test_company_specific_threshold_overwrite_default(self):
        partner = self._create_partner("Customer Company Specific", self.company_vip_10000)
        self.company_vip_10000.write({"vip_threshold": 50000.0})
        invoice = self._create_invoice(partner, 45000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
        self.assertFalse(partner.is_vip)

        # Reset the threshold for the next tests
        self.company_vip_10000.write({"vip_threshold": 10000.0})

    def test_changing_threshold_affects_existing_customers(self):
        partner = self._create_partner("Customer Dynamic Threshold", self.company_vip_10000)
        invoice = self._create_invoice(partner, 12000.0)
        invoice.action_post()
        self._pay_invoice(invoice)
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
        self._pay_invoice(invoice1)
        self.assertFalse(partner.is_vip)

        partner.invalidate_recordset()

        invoice2 = self._create_invoice(partner, 3000.0)
        invoice2.action_post()
        self._pay_invoice(invoice2)
        partner.invalidate_recordset()
        self.assertTrue(partner.is_vip)

    def test_vip_threshold_allows_zero(self):
        partner = self._create_partner(
            "Customer Zero Threshold", self.company_vip_10000)
        self.company_vip_10000.write({"vip_threshold": 0.0})
        self.assertEqual(self.company_vip_10000.vip_threshold, 0.0)

    def test_vip_threshold_rejects_negative(self):
        company_form = Form(self.company_vip_10000)
        with self.assertRaises(ValidationError):
            company_form.vip_threshold = -500.0

    def test_non_accounting_user_vip_computation_is_vip(self):
        invoice = self._create_invoice(self.partner, 50000.0)
        invoice.action_post()
        self._pay_invoice(invoice)

        non_accounting_user = self.partner.with_user(self.non_accounting_user)
        self.assertTrue(non_accounting_user.is_vip)

    def test_non_accounting_user_vip_computation_not_vip(self):
        invoice = self._create_invoice(self.partner, 5000.0)
        invoice.action_post()
        self._pay_invoice(invoice)

        non_accounting_user = self.partner.with_user(self.non_accounting_user)
        self.assertFalse(non_accounting_user.is_vip)

    def test_non_accounting_user_cannot_change_threshold(self):
        company_as_basic = self.company_vip_10000.with_user(
            self.non_accounting_user)

        with self.assertRaises(AccessError):
            company_as_basic.write({"vip_threshold": 25000.0})

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
        company_id = partner.company_id.id if partner.company_id else self.env.company.id

        # Find(Demo)/Create(Blank) income account
        income_account = self.env["account.account"].search([
            ("account_type", "=", "income"),
            ("company_ids", "in", [company_id])
        ], limit=1)

        if not income_account:
            income_account = self.env["account.account"].sudo().create({
                "name": "Test Income Account",
                "code": f"INC.{company_id}",
                "account_type": "income",
                "company_ids": [Command.link(company_id)],
            })

        # Find(Demo)/Create(Blank) Receivable Account
        receivable_account = self.env["account.account"].search([
            ("account_type", "=", "asset_receivable"),
            ("company_ids", "in", [company_id])
        ], limit=1)

        if not receivable_account:
            receivable_account = self.env["account.account"].sudo().create({
                "name": "Test Receivable Account",
                "code": f"REC.{company_id}",
                "account_type": "asset_receivable",
                "company_ids": [Command.link(company_id)],
                "reconcile": True,
            })

        # Use found/created receivable account
        partner.with_company(
            company_id).property_account_receivable_id = receivable_account

        # Create Invoice
        invoice = self.env["account.move"].with_user(self.accounting_user).create({
            "partner_id": partner.id,
            "move_type": "out_invoice",
            "invoice_line_ids" : [Command.create({
                "name": "Test Invoice Line",
                "quantity": 1,
                "price_unit": amount,
                "account_id": income_account.id,
            })],
        })
        return invoice

    def _pay_invoice(self, invoice):
        ctx = {'active_model': 'account.move', 'active_ids': invoice.ids}
        payment_register = self.env['account.payment.register'].with_user(
            self.accounting_user).with_context(ctx).create({})
        payment_register._create_payments()
