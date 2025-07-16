# -*- coding: utf-8 -*-
from odoo import fields, models


class Events(models.Model):
    """Model that represents university events"""
    _name = 'events'
    _description = 'Event'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "event_name"

    university_id = fields.Many2one('university', string='University Name', required=True)
    university_code = fields.Char(string='University Code', related='university_id.code')
    university_type = fields.Selection(string='University Type', related='university_id.type')
    event_name = fields.Char(string='Event Name', required=True)
    event_type = fields.Selection(
        [('seminar', 'Seminar'), ('cultural_event', 'Cultural Events'), ('exhibition', 'Exhibition'),
         ('sports', 'Sports')], string='Event Type')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    event_line_ids = fields.One2many('event.lines', 'event_id', string='Event Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('expired', 'Expired')
    ], string='Status', default='draft', tracking=True)
