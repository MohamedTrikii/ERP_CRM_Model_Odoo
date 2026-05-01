# -*- coding: utf-8 -*-
{
    'name': 'ERP PROJECT IIT (CRM) MT & IB',
    'version': '19.0.2.0.0',
    'category': 'Sales/CRM',
    'sequence': 15,
    'summary': 'AI-powered CRM with pipeline, scoring, stock simulation and automations',
    'description': """
ERP PROJECT IIT (CRM) MT & IB Module
======================================

Key Features:
-------------
* AI Lead Scoring (0–100) based on activity, revenue, priority
* Automatic Client Segmentation (VIP, Loyal, At-Risk, Cold, New)
* Risk Level Detection (Low / Medium / High)
* Kanban with live score badges, progress bar, segment colours
* Product Stock simulation with auto-purchase trigger
* Cron jobs: inactive lead alert, low stock check, score recompute
* Server actions: auto follow-up, risk detection
* Full security groups: User / Sales / Purchase / Manager

    """,
    'author': 'CRM_TRIKI ERP — Open Source',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'utm',
        'product',
        'sale',
        'purchase',
    ],
    'data': [
        # Model declarations (must be first)
        'data/crm_mt_model.xml',

        # Security
        'security/crm_mt_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/crm_mt_data.xml',
        'data/crm_mt_automation.xml',

        # Views
        'views/crm_mt_team_views.xml',
        'views/crm_mt_stage_views.xml',
        'views/crm_mt_lost_reason_views.xml',
        'views/crm_mt_lead_views.xml',
        'views/crm_mt_sale_views.xml',
        'views/crm_mt_sale_line_views.xml',
        'views/crm_mt_purchase_views.xml',
        'views/crm_mt_purchase_line_views.xml',
        'views/crm_mt_dashboard_views.xml',

        # Menus (must be last)
        'views/crm_mt_menus.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.00,
    'currency': 'EUR',
}

