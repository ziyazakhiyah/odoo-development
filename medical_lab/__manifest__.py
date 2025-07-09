# -*- coding: utf-8 -*-
{
    'name': "Appointment Management",
    'version': '18.0.1.0.0',
    'category': 'Industries',
    'summary': """Manage Medical Lab Operations.""",
    'description': """Manage Medical Laboratory Operations,Manage Appointments.""",
    'author': "Cybrosys Techno Solutions",
    'company': "Cybrosys Techno Solutions",
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/lab_appointment_sequence.xml',
        'data/lab_patient_sequence.xml',
        'data/lab_stage.xml',
        'views/lab_patient_views.xml',
        'views/lab_appointment_views.xml',
        'views/lab_stage_views.xml',
        'views/client_action.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'medical_lab/static/src/js/form.js',
            'medical_lab/static/src/js/style.css',
            'medical_lab/static/src/js/welcomedash.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
