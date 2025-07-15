# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import http
from odoo.http import request


class EventController(http.Controller):
    @http.route('/my/events', type='http', auth='user', website=True)
    def portal_my_events(self):
        today = datetime.today().date()
        three_months_later = today + relativedelta(months=3)
        events = request.env['events'].sudo().search([
            ('start_date', '>=', today),
            ('start_date', '<=', three_months_later),
        ])
        return request.render('upcoming_events.portal_events', {
            'events': events,
        })
