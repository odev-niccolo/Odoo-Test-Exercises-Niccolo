# -*- coding: utf-8 -*-
from odoo import models, fields

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

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################