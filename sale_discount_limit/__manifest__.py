# -*- coding: utf-8 -*-
{
    'name': 'Discount Limit',
    'version': '18.0.0.1',
    'summary': 'Add discount limit for sales order',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_discount_limit_views.xml',
        'views/res_config_settings_views.xml',
        'views/cart_lines.xml',
    ],
    'depends': ['sale','sale_management', 'website_sale'],

    'assets': {
        'web.assets_frontend': [
            'sale_discount_limit/static/src/js/cart.js',
        ],
    },
}