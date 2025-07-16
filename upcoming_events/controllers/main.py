# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import http
from odoo.http import request


class EventController(http.Controller):

    @http.route('/my/events', type='http', auth='user', website=True)
    def portal_my_events(self, **kw):
        today = datetime.today().date()
        three_months_later = today + relativedelta(months=3)
        sortby = kw.get('sortby', 'date')
        filterby = kw.get('filterby', 'all')
        event_type = kw.get('event_type')
        groupby = kw.get('groupby') or 'none'
        event_type_selection = dict(request.env['events']._fields['event_type'].selection)
        searchbar_sortings = {
            'date': {'label': 'Date'},
            'name': {'label': 'Name'},
        }
        searchbar_filters = {
            'all': {'label': 'All'},
            'upcoming': {'label': 'Upcoming'},
            'past': {'label': 'Past'},
        }
        domain = []
        if filterby == 'upcoming':
            domain += [('start_date', '>=', today), ('start_date', '<=', three_months_later)]
        elif filterby == 'past':
            domain += [('end_date', '<', today)]
        elif filterby == 'type' and event_type:
            domain += [('event_type', '=', event_type)]
        else:
            domain += [('start_date', '>=', today), ('start_date', '<=', three_months_later)]
        order = 'start_date desc' if sortby == 'date' else 'event_name asc'
        events = request.env['events'].search(domain, order=order)
        values = {
            'title': 'Upcoming Events',
            'events': events,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
            'groupby': groupby,
            'default_url': '/my/events',
            'breadcrumbs_searchbar': True,
            'event_type_selection': event_type_selection,
            'event_type': event_type,
        }
        return request.render('upcoming_events.portal_events', values)
