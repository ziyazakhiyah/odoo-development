# -*- coding: utf-8 -*-
from odoo import models,fields,api


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = "pos.load.mixin"

    name = fields.Char()

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name']
