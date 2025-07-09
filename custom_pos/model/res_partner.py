# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'pos.load.mixin']

    pos_order_ids = fields.One2many('pos.order', 'partner_id', string="POS Orders")
    pos_orders_amount_due = fields.Float(string="Amount Due", compute='_compute_pos_orders_amount_due')

    @api.depends('pos_order_ids.amount_total', 'pos_order_ids.state')
    def _compute_pos_orders_amount_due(self):
        print('_compute_pos_orders_amount_due')
        for partner in self:
            payments = self.env['pos.payment'].search([
                ('payment_method_id.type', '=', 'pay_later'),
                ('pos_order_id.partner_id', '=', partner.id),
                ('pos_order_id.state', 'not in', ['invoiced', 'done']),
            ])
            partner.pos_orders_amount_due = sum(payments.mapped('amount'))

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Function to load field into POS"""
        fields = super()._load_pos_data_fields(config_id)
        fields.append('pos_orders_amount_due')
        return fields
