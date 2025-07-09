# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import UserError


class POSOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create(self, vals):
        self._check_customer_due_limit(vals)
        return super().create(vals)

    def _check_customer_due_limit(self, vals):
        partner_id = vals.get('partner_id')
        amount_total = vals.get('amount_total', 0.0)
        partner = self.env['res.partner'].browse(partner_id)
        current_due = partner.pos_orders_amount_due or 0.0
        limit = self.env['ir.config_parameter'].sudo().get_param('custom_pos.customer_due_limit', default='0.0')
        try:
            due_limit = float(limit)
        except ValueError:
            due_limit = 0.0
        if (current_due + amount_total) > due_limit:
            raise UserError((
                f"Cannot confirm order. Customer's due ({current_due + amount_total:.2f}) exceeds allowed limit of {due_limit:.2f}."
            ))
