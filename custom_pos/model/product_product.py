# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one(related='product_tmpl_id.brand_id', string="Brand", store=True)

    def _load_pos_data_fields(self, config_id):
        """To load the field brand_id to POS"""
        result = super()._load_pos_data_fields(config_id)
        result.append('brand_id')
        return result

    def _pos_ui_product_fields(self):
        """ Adds 'brand_id' to the list of product fields sent to the frontend"""
        return super()._pos_ui_product_fields() + ['brand_id']
