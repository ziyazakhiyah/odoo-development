# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    """Inheriting settings to add sales report settings"""
    _inherit = 'res.config.settings'

    frequency = fields.Selection([('monthly', 'Monthly'), ('weekly', 'Weekly'), ], string='Frequency',
                                 default='monthly', config_parameter='monthly_weekly_sales_report.frequency')
    customer_ids = fields.Many2many('res.partner', string="Customers")
    sales_team_ids = fields.Many2many('crm.team', string="Sales Team")
    from_date = fields.Datetime(string="From Date", config_parameter='monthly_weekly_sales_report.from_date')
    to_date = fields.Datetime(string="To Date", config_parameter='monthly_weekly_sales_report.to_date')

    def set_values(self):
        """Function that is used to set values in settings"""
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        customer_ids_str = ','.join(str(id) for id in self.customer_ids.ids)
        sales_team_ids_str = ','.join(str(id) for id in self.sales_team_ids.ids)
        param.set_param('monthly_weekly_sales_report.customer_ids', customer_ids_str)
        param.set_param('monthly_weekly_sales_report.sales_team_ids', sales_team_ids_str)
        return True

    @api.model
    def get_values(self):
        """Function that is used to fetch values in settings form"""
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        customer_ids_str = param.get_param('monthly_weekly_sales_report.customer_ids', '')
        sales_team_ids_str = param.get_param('monthly_weekly_sales_report.sales_team_ids', '')
        customer_ids = [int(id) for id in customer_ids_str.split(',') if id]
        sales_team_ids = [int(id) for id in sales_team_ids_str.split(',') if id]
        res.update(
            customer_ids=[(6, 0, customer_ids)],
            sales_team_ids=[(6, 0, sales_team_ids)]
        )
        return res
