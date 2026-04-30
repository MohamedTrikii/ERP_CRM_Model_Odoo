# -*- coding: utf-8 -*-
{
    'name': 'Flowmerce ERP — Purchase Management',
    'version': '19.0.2.0.0',
    'category': 'Purchase/Purchase',
    'summary': 'Purchase orders, supplier scoring, delivery risk and auto-order',
    'description': """
        Flowmerce ERP — Purchase Management
        =====================================
        * RFQ and Purchase Order management
        * Supplier Score (AI computed, 0–100)
        * Delivery Risk level (Low / Medium / High)
        * Auto-Order flag: auto-confirm POs for low-stock replenishment
        * Expected vs Actual delivery date tracking
        * Line-level discount support
        * Dashboard: spend by supplier, delivery risk distribution
        * Cron: auto-confirm flagged POs
    """,
    'author': 'Flowmerce ERP — Open Source',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'uom', 'crm_mt'],
    'data': [
        'security/ir.model.access.csv',
        'data/purchase_data.xml',
        'views/purchase_order_views.xml',
        'views/purchase_dashboard_views.xml',
        'views/purchase_menu.xml',
    ],
    'demo': [
        'data/purchase_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 20,
}
