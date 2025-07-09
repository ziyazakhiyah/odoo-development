# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Model to add discount limit setting to sales"""
    _inherit = 'res.config.settings'

    discount_limit = fields.Float(string="Discount Limit", config_parameter="sale_discount_limit.discount_limit")