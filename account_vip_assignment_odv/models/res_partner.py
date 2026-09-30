# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "res.partner"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    is_vip = fields.Boolean(string="VIP Customer",
                            compute="_compute_is_vip")
    
    ##############################
    # Compute and search methods #
    ##############################
    @api.depends("invoice_ids.state", "invoice_ids.amount_total", "company_id.vip_threshold")
    def _compute_is_vip(self):
        for partner in self:
            threshold = (partner.company_id.vip_threshold
                     if partner.company_id else 10000.0)
            
            domain = [
                ("move_type", "=", "out_invoice"),
                ("partner_id", "=", partner.id),
                ("state", "=", "posted"),

            ]
            if partner.company_id:
                domain.append(("company_id", "in", [partner.company_id.id, False]))

            invoices = self.env["account.move"].sudo().search(domain)
            partner.is_vip = sum(invoices.mapped("amount_total")) >= threshold
            
    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################