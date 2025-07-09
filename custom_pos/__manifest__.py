# -*- coding: utf-8 -*-
{
    'name': 'Custom POS',
    'version': '18.0.0.1',
    'summary': 'Add brand to Order',
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'depends': ['point_of_sale', 'base', 'product', 'web'],
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_pos/static/src/js/pos_orderline.js',
            'custom_pos/static/src/js/clear_orderlines.js',
            'custom_pos/static/src/xml/product_brand_view.xml',
            'custom_pos/static/src/xml/clear_orderlines.xml',
            'custom_pos/static/src/xml/partner_list.xml',
            'custom_pos/static/src/xml/partner_line.xml',
        ],
    },
}
