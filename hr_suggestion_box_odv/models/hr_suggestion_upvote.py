# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrSuggestionUpvote(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.suggestion.upvote"
    _description = "Employee Suggestion Upvote"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    user_id = fields.Many2one(comodel_name="res.users",
                              string="User",
                              required=True,
                              default=lambda self: self.env.user)
    hr_suggestion_id = fields.Many2one(comodel_name="hr.suggestion",
                                       string="Suggestion",
                                       required=True,
                                       ondelete="cascade")

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    @api.constrains("user_id")
    def _check_user_id(self):
        for suggestion_upvote in self:
            if not suggestion_upvote.user_id.employee_id:
                raise ValidationError(
                    _("You must be an employee to upvote a suggestion.")
                )

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
