# -*- coding: utf-8 -*-
{
    'name': 'HR Hub',
    'version': '18.0.1.0.0',
    'summary': 'HR Hub',
    'description': "HR Hub",
    'category': 'Human Resources',
    'author': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_hiring_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': False,
    'installable': True,
    'application': True,
}
