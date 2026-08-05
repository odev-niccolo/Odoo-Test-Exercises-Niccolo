# -*- coding: utf-8 -*-
{
    "name": "Employee Suggestion Box",
    "sequence": 0,
    "version": "19.0.1.0",
    "depends": [
        "hr"
    ],
    "external_dependencies": {},
    "author": "Odev Solutions",
    "website": "https://www.odevsolutions.com",
    "summary": """Employee Suggestion Box""",
    "description": """
        Employee Suggestion Box
    """,
    "category": "Human Resources",
    "data": [
        "security/hr_suggestion_groups.xml",
        "security/ir.model.access.csv",
        "views/hr_suggestion_views.xml"
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_common": [],
        "web.qunit_suite_tests": [],
    },
    "qweb": [],
    "css": [],
    "images": [],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
}