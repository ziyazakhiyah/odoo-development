# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    """Model to view partners"""
    _inherit = 'res.partner'

    property_ids = fields.One2many('property', 'owner_id', string="Properties")
    number_related_properties = fields.Integer(compute='_compute_number_related_properties')

    @api.depends()
    def _compute_number_related_properties(self):
        """Function to calculate total related number of properties"""
        for rec in self:
            rec.number_related_properties = self.env['property'].search_count([('owner_id', '=', self.id)])

    def action_open_related_properties(self):
        """Button to view related properties"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Property",
            'res_model': 'property',
            'domain': [('owner_id', '=', self.id)],
            'view_mode': 'list,form',
        }
