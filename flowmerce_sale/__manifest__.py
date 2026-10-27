# -*- coding: utf-8 -*-
{
    'name': 'Flowmerce ERP — Sales Management',
    'version': '19.0.2.0.0',
    'category': 'Sales/Sales',
    'summary': 'Sales orders, margin tracking, payment status and automated follow-up',
    'description': """
        Flowmerce ERP — Sales Management
        =================================
        * Quotation and sale order management
        * Margin & margin rate per line and order
        * Global discount on orders
        * Payment status tracking (Unpaid / Partial / Paid)
        * Auto-confirm and auto-invoice actions
        * Cron: stale quotation follow-up
        * Dashboard: revenue, margin by month/salesperson
    """,
    'author': 'Flowmerce ERP — Open Source',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'uom', 'crm_mt'],
    'data': [
        'security/sales_security.xml',
        'security/ir.model.access.csv',
        'data/sales_data.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_dashboard_views.xml',
        'views/res_partner_views.xml',
        'views/sale_menus.xml',
        'report/sale_report_templates.xml',
        'wizard/sale_invoice_wizard_views.xml',
    ],
    'demo': [
        'data/sales_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
}