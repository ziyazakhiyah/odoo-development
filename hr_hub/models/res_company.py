# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_hiring_reviewer_ids = fields.Many2many('res.users', 'res_company_hr_reviewer_rel',
                                              'company_id', 'user_id', string="HR Reviewers")