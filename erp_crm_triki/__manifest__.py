# -*- coding: utf-8 -*-
{
    'name': 'ERP CRM Triki',
    'version': '1.0',
    'category': 'Sales/CRM',
    'summary': 'Suite ERP complète : CRM, Vente, Achat',
    'author': 'Triki',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'utm', 'product', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/erp_crm_triki_security.xml',
        'data/erp_crm_triki_sequence.xml',
        'data/erp_crm_triki_demo.xml',
        'views/erp_crm_triki_menus.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/crm_dashboard_views.xml',
        'views/sale_dashboard_views.xml',
        'views/purchase_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'description': 'ERP Odoo 19 tout-en-un : CRM, Vente, Achat, dashboards, sécurité, automatisations, tests.'
}
