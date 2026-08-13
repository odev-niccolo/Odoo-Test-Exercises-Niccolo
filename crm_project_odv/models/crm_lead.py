# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmLead(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "crm.lead"
    
    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    project_id = fields.Many2one(comodel_name="project.project", 
                                 string="Project", 
                                 readonly=True)
    
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