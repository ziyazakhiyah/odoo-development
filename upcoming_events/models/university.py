# -*- coding: utf-8 -*-
from odoo import api, fields, models


class University(models.Model):
    """ This model represents university."""
    _name = 'university'
    _description = 'University'

    name = fields.Char(string='University Name', required=True)
    code = fields.Char(string='University Code', required=True)
    type = fields.Selection([('private', 'Private'),('public', 'Public')], string='University type')