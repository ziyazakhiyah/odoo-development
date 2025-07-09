# -*- coding: utf-8 -*-
from odoo import models,api


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config_id):
        """load the data to the pos.config.models"""
        data = super()._load_pos_data_models(config_id)
        data += ['product.brand']
        return data
