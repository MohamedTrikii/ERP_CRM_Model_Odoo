# -*- coding: utf-8 -*-
{
    'name': 'ERP Sales Management',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Module complet de gestion des ventes avec devis, commandes et facturation',
    'description': """
        Module de Gestion des Ventes
        ============================
        * Gestion des devis et commandes clients
        * Conversion automatique devis → commande
        * Génération de factures
        * Suivi des statuts (brouillon, confirmé, livré, facturé)
        * Dashboard analytique des ventes
        * Rapports et statistiques
    """,
    'author': 'Votre Entreprise',
    'website': 'https://www.votreentreprise.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product'],
    'data': [
        'security/sales_security.xml',
        'security/ir.model.access.csv',
        'data/sales_data.xml',
        'data/sales_demo.xml',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
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