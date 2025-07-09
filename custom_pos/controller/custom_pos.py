# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class POSDueLimitController(http.Controller):

    @http.route('/pos/get_customer_due', type='json', auth='public', csrf=False)
    def get_customer_due(self, partner_id):
        partner = request.env['res.partner'].browse(int(partner_id))
        return {
            'partner_id': partner.id,
            'pos_orders_amount_due': partner.pos_orders_amount_due or 0.0,
        }
