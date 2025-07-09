# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_due_limit = fields.Float(
        string="Customer Due Limit",
        help="Maximum allowed due amount per customer."
    )

    @api.model
    def get_values(self):
        """Fetch saved settings from ir.config_parameter."""
        res = super(ResConfigSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        customer_due_limit = icp_sudo.get_param('custom_pos.customer_due_limit', default='0.0')
        res.update(
            customer_due_limit=float(customer_due_limit)
        )
        return res

    def set_values(self):
        """Store settings to ir.config_parameter."""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'custom_pos.customer_due_limit', self.customer_due_limit
        )
        return res

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Function to load field into POS"""
        fields = super()._load_pos_data_fields(config_id)
        fields.append('customer_due_limit')
        return fields
