# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveLine(models.Model):
    """Inheriting account.move.line model for invoice lines"""
    _inherit = 'account.move.line'

    property_line_id = fields.Many2one('rent.move.line', string="Property Line")