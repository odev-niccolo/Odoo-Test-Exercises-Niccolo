# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

@tagged("post_install", "-at_install", "test_hr_suggestion")
class TestHrSuggestionBox(TransactionCase):
    
    ######################
    # Setup              #
    ######################
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context))

        # Setup Groups
        cls.group_user = cls.env.ref("base.group_user")
        cls.group_manager = cls.env.ref("hr_suggestion_box_odv.group_hr_suggestion_manager")

        # Setup Users
        cls.normal_employee = cls.env["res.users"].create({
            "name": "Normal Employee",
            "login": "normal_employee",
            "email": "normal_employee@mail.com",
            "group_ids": [(6, 0, [cls.group_user.id])]
        })

        cls.upvote_employee = cls.env["res.users"].create({
            "name": "Upvote Employee",
            "login": "upvote_employee",
            "email": "upvote_employee@mail.com",
            "group_ids": [(6, 0, [cls.group_user.id])]
        })
        
        manager_groups = [cls.group_user.id, cls.group_manager.id]

        cls.suggestion_approver = cls.env["res.users"].create({
            "name": "Suggestion Approver",
            "login": "suggestion_approver",
            "email": "suggestion_approver@mail.com",
            "group_ids": [(6, 0, manager_groups)]
        })

        # Setup Employees
        cls.env["hr.employee"].create([
            {"name": "Normal Employee", "user_id": cls.normal_employee.id},
            {"name": "Upvote Employee", "user_id": cls.upvote_employee.id},
            {"name": "Suggestion Approver", "user_id": cls.suggestion_approver.id},
        ])

    

    ######################
    # Unit Tests         #
    ######################
    def test_default_state(self):
        """ Verify default state upon creation is draft """
        suggestion = self._create_suggestion(self.normal_employee)
        self.assertEqual(suggestion.state, "draft")

    def test_action_confirm(self):
        """ Verify action_confirm transitions state to ready_for_upvote """
        suggestion = self._create_suggestion(self.normal_employee)
        suggestion.action_confirm()
        self.assertEqual(suggestion.state, "ready_for_upvote")

    def test_action_approve(self):
        """ Verify action_approve transitions state to approved """
        suggestion = self._create_suggestion(self.normal_employee)
        suggestion.action_confirm()
        suggestion.with_user(self.suggestion_approver).action_approve()
        self.assertEqual(suggestion.state, "approved")

    def test_action_reject(self):
        """ Verify action_reject transitions state to rejected """
        suggestion = self._create_suggestion(self.normal_employee)
        suggestion.action_confirm()
        suggestion.with_user(self.suggestion_approver).action_reject()
        self.assertEqual(suggestion.state, "rejected")

    def test_invalid_state_approval(self):
        """ Verify validation error is raised when suggestion approver tries to approve a draft suggestion """
        suggestion = self._create_suggestion(self.normal_employee)
        
        with self.assertRaises(ValidationError):
            suggestion.with_user(self.suggestion_approver).action_approve()

    def test_author_upvote_constraint(self):
        """ Verify validation error is raised if author attempts to upvote their own suggestion """
        suggestion = self._create_suggestion(self.normal_employee)
        suggestion.action_confirm()
        
        with self.assertRaises(ValidationError):
            suggestion.with_user(self.normal_employee).action_upvote()

    def test_multiple_upvote_constraint(self):
        """ Verify validation error is raised if a user attempts to upvote more than once """
        suggestion = self._create_suggestion(self.normal_employee)
        suggestion.action_confirm()
        

        # First upvote should succeed
        suggestion.with_user(self.upvote_employee).action_upvote()
        self.assertEqual(suggestion.hr_suggestion_upvote_count, 1)

        # Second upvote should raise ValidationError
        with self.assertRaises(ValidationError):
            suggestion.with_user(self.upvote_employee).action_upvote()

    ######################
    # E2E Tests          #
    ######################    

    ######################
    # Helper Methods     #
    ######################
    def _create_suggestion(self, user):
        """ Helper method to create a suggestion record quickly """
        return self.env["hr.suggestion"].with_user(user).create({
            "name": "Isolated Test Suggestion",
            "description": "Default test description."
        })