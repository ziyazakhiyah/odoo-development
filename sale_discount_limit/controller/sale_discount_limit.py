# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class CartController(http.Controller):
    @http.route('/shop/clear_cart', type='json', auth='user', website=True)
    def clear_cart(self):
        order = request.website.sale_get_order()
        if order:
            order.order_line.unlink()
        return {'status': 'success'}