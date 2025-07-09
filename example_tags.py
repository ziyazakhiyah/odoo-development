# -*- coding: utf-8 -*-
from random import randint
from odoo import models, fields, api


class ExampleTags(models.Model):
    """Model for creating tags"""

    _name = 'example.tags'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color', default=_get_default_color)
