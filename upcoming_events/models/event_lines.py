# -*- coding: utf-8 -*-
from odoo import fields, models


class EventLines (models.Model):
    """ This model represents event lines"""
    _name = 'event.lines'
    _description = 'event lines with time slots and content'

    content = fields.Char(string='Event', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    event_id = fields.Many2one('events', string='Event')
