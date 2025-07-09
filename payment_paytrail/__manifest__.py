# -*- coding: utf-8 -*-
{
    'name': "Payment Provider: Paytrail Payment Gateway",
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 5,
    'summary': "Paytrail Payment Gateway for Odoo",
    'description': "Paytrail Payment Gateway for Odoo",
    'depends': ['base', 'payment'],
    'images': [
            'static/description/icon.png'
    ],
    'data': [
        'views/payment_paytrail_templates.xml',
        'data/payment_provider_data.xml',
        'data/payment_method_data.xml',
        'views/payment_provider_views.xml',
    ],
    'web_icon': 'static/description/icon.png',
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
