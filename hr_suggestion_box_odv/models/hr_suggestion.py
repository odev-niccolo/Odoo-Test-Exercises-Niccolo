# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import ValidationError


class HrSuggestion(models.Model):
    ######################
    # Private attributes #
    ######################
    _name = "hr.suggestion"
    _description = "Employee Suggestion Box"
    _order = "create_date desc"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    name = fields.Char(string="Title",
                       required=True)
    description = fields.Html(string="Description")
    state = fields.Selection(selection=[("draft", "Draft"),
                                        ("ready_for_upvote", "Ready for Upvote"),
                                        ("approved", "Approved"),
                                        ("rejected", "Rejected")],
                             string="State",
                             required=True,
                             default="draft")
    user_id = fields.Many2one(comodel_name="res.users",
                              string="User",
                              required=True,
                              default=lambda self: self.env.user)
    hr_suggestion_upvote_ids = fields.One2many(comodel_name="hr.suggestion.upvote",
                                               string="Upvotes",
                                               inverse_name="hr_suggestion_id")
    hr_suggestion_upvote_count = fields.Integer(string="Upvote Count",
                                                compute="_compute_hr_suggestion_upvote_count")
    can_approve = fields.Boolean(compute="_compute_can_approve")

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    def _compute_hr_suggestion_upvote_count(self):
        for suggestion in self:
            suggestion.hr_suggestion_upvote_count = len(suggestion.hr_suggestion_upvote_ids)

    def _compute_can_approve(self):
        for suggestion in self:
            if suggestion.state == "ready_for_upvote":
                suggestion.can_approve = bool(self.env.user.has_group("hr_suggestion_box_odv.group_hr_suggestion_manager"))
            else:
                suggestion.can_approve = False

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################
    def action_confirm(self):
        self.write({"state": "ready_for_upvote"})

    def action_reset_draft(self):
        has_upvote = self.hr_suggestion_upvote_ids
        if has_upvote:
            raise ValidationError(
                _("You cannot reset a suggestion that has been upvoted.")
            )
        self.write({"state": "draft"})

    def action_approve(self):
        has_no_ready = self.filtered(lambda x: x.state not in ["ready_for_upvote"])
        if has_no_ready:
            raise ValidationError(
                _("You cannot approve a suggestion that is not ready for approval.")
            )
        self.write({"state": "approved"})

    def action_reject(self):
        has_no_ready = self.filtered(lambda x: x.state not in ["ready_for_upvote"])
        if has_no_ready:
            raise ValidationError(
                _("You cannot reject a suggestion that is in a state other than 'ready for upvote'.")
            )
        self.write({"state": "rejected"})

    def action_upvote(self):
        self.ensure_one()

        if self.user_id.id == self.env.uid:
            raise ValidationError(
                _("You cannot upvote your own suggestion.")
            )

        if self.state != "ready_for_upvote":
            raise ValidationError(
                _("You cannot upvote a suggestion that is not ready for upvote.")
            )

        if self.hr_suggestion_upvote_ids.filtered(lambda x: x.user_id.id == self.env.uid):
            raise ValidationError(
                _("You have already upvoted this suggestion.")
            )

        self.hr_suggestion_upvote_ids.create({
            "hr_suggestion_id": self.id,
            "user_id": self.env.uid,
        })

    ####################
    # Business methods #
    ####################
