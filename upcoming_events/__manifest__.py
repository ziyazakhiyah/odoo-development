# -*- coding: utf-8 -*-
{
    'name': 'Upcoming Events',
    'version': '1.0',
    'summary': 'Upcoming Events',
    'description': '''
        Upcoming Events
    ''',
    'category': 'Uncategorized',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/university_data.xml',
        'views/events_views.xml',
        'views/events_portal_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}