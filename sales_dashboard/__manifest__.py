# -*- coding: utf-8 -*-
{
    'name': 'Sales Dashboard',
    'version': '1.0',
    'summary': 'Custom Sales Dashboard with Key Metrics',
    'description': 'Displays sales by team and person, top customers, best and worst selling products, order and invoice statuses.',
    'category': 'Sales',
    'depends': ['base', 'sale_management', 'account', 'web'],
    'data': [
        'views/sales_dashboard_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sales_dashboard/static/src/js/sales_dashboard.js',
            'sales_dashboard/static/src/xml/sales_dashboard_templates.xml'
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
