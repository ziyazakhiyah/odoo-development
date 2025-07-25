# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_hiring_reviewer_ids = fields.Many2many(comodel_name='res.users',
                                              related='company_id.hr_hiring_reviewer_ids', readonly=False)
