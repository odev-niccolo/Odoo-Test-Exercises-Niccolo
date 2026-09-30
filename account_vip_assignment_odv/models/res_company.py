# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "res.company"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    vip_threshold = fields.Float(string="VIP Threshold",
                                 default=10000.0)
    
    ##############################
    # Compute and search methods #
    ##############################
            
    ############################
    # Constrains and onchanges #
    ############################
    @api.onchange('vip_threshold')
    def _onchange_vip_threshold(self):
        if self.vip_threshold < 0:
            raise ValidationError(_("The VIP Threshold can't be negative."))

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################