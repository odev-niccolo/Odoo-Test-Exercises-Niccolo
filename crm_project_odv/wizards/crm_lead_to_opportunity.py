# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmLead2opportunityPartner(models.TransientModel):
    ######################
    # Private attributes #
    ######################
    _inherit = "crm.lead2opportunity.partner"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    create_project = fields.Boolean("Create Project")

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
    def _convert_and_allocate(self, leads, user_ids, team_id=False):
        res = super(CrmLead2opportunityPartner, self)._convert_and_allocate(leads, user_ids, team_id=team_id)
        if self.create_project:
            for lead in leads:
                project = self.env["project.project"].create({
                    "name": lead.name,
                    "partner_id": lead.partner_id.id
                })
                lead.write({"project_id": project.id})
        return res