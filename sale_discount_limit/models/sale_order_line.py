# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    """Inheriting sale.order.line model for sale order lines"""
    _inherit = 'sale.order.line'

    price_wo_discount = fields.Float(string="Discount Excluded", compute="_compute_price_wo_discount")

    @api.depends('price_total', 'discount')
    def _compute_price_wo_discount(self):
        for rec in self:
            rec.price_wo_discount = (rec.price_unit + ((rec.tax_id.amount/100) * rec.price_unit)) * rec.product_uom_qty
