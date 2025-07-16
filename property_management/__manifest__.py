# -*- coding: utf-8 -*-
{
    'name': 'Property Management',
    'version': '18.0.0.1',
    'summary': 'Manage Properties',
    'application': True,
    'sequence': 1,
    'data': [
        'security/res_groups.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'data/property_data.xml',
        'data/sequence_data.xml',
        'data/mail_data.xml',
        'data/ir_cron.xml',
        'data/report_paperformat_data.xml',
        'wizard/contract_generate_report.xml',
        'views/facilities_views.xml',
        'views/property_views.xml',
        'views/contract_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/property_management_menus.xml',
        'views/website_form_template.xml',
        'views/contract_portal_templates.xml',
        'views/snippets/properties_template.xml',
        'views/snippets/property_detail_page.xml',
        'views/snippets/properties_webpage.xml',
        'report/report.xml',
        'report/contract_report_template.xml',
    ],
    'depends': ['base', 'mail', 'account', 'website', 'web'],
    'assets': {
        'web.assets_backend': [
            'property_management/static/src/js/action_manager.js',
            'property_management/static/src/css/property_management.css'
        ],
        'web.assets_frontend': [
            'property_management/static/src/js/contract_form.js',
            'property_management/static/src/js/property_snippet.js',
            'property_management/static/src/xml/properties_data.xml',

        ],
    },
}
