# -*- coding: utf-8 -*-
{
    "name": "Project Auto-Creation from Lead",
    "sequence": 0,
    "version": "19.0.1.0",
    "depends": [
        "crm",
        "project"
    ],
    "external_dependencies": {},
    "author": "Odev Solutions",
    "website": "https://www.odevsolutions.com",
    "summary": """Project Auto-Creation from Lead""",
    "description": """
        Project Auto-Creation from Lead
    """,
    "category": "Sales",
    "data": [
        "wizards/crm_lead_to_opportunity_views.xml",
        "views/crm_lead_views.xml"
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
    "application": False,
    "auto_install": False,
}