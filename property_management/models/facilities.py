# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Facilities(models.Model):
    """Model containing facilities of properties"""
    _name = 'facilities'
    _description = 'Facilities of properties'

    name = fields.Char(string="Facility")
    number_related_properties = fields.Integer(compute='_compute_number_related_properties')

    @api.depends()
    def _compute_number_related_properties(self):
        """Function to calculate total related number of properties"""
        for rec in self:
            rec.number_related_properties = self.env['property'].search_count([('facilities_ids', '=', self.id)])

    def action_open_related_properties(self):
        """Button to view related properties"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Property",
            'res_model': 'property',
            'domain': [('facilities_ids', '=', self.id)],
            'view_mode': 'list,form',
        }
