# -*- coding: utf-8 -*-
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleDiscountLimit(models.Model):
    """Inheriting sale.order model for adding discount limit"""
    _inherit = 'sale.order'

    discount_amount = fields.Float(string="Discount Amount", compute="_compute_discount_amount")

    @api.depends('amount_total')
    def _compute_discount_amount(self):
        for rec in self:
            total_amount_wo_discount = sum(rec.order_line.mapped('price_wo_discount'))
            rec.discount_amount = total_amount_wo_discount - rec.amount_total

    def action_confirm(self):
        for rec in self:
            today = date.today()
            start_month = today.replace(day=1)
            end_month = (start_month + relativedelta(months=1)) - relativedelta(days=1)

            orders_in_month = self.env['sale.order'].search([
                ('create_date', '>=', start_month),
                ('create_date', '<=', end_month),
                ('state', '=', 'sale'),
                ('id', '!=', rec.id)
            ])
            total_discount = sum(orders_in_month.mapped('discount_amount')) + rec.discount_amount

            limit = float(self.env['ir.config_parameter'].sudo().get_param('sale_discount_limit.discount_limit', 0.0))
            if total_discount > limit:
                raise ValidationError('Monthly discount limit exceeded. Cannot confirm this order.')

        return super().action_confirm()

