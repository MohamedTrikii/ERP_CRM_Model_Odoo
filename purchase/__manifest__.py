{
    'name': 'Purchase',
    'version': '1.0',
    'summary': 'Gestion des achats',
    'author': 'Votre Nom',
    'category': 'Purchases',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_menu.xml',
        'data/purchase_demo.xml',
    ],
    'demo': ['data/purchase_demo.xml'],
    'installable': True,
    'application': True,
}
