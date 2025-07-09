# -*- coding: utf-8 -*-
from odoo import models, fields


class LabStage(models.Model):
    _name = 'lab.stage'
    _description = 'Lab Stage'

    name = fields.Char(required=True)
    is_folded = fields.Boolean(default=False)
    show_in_view = fields.Boolean(default=False)