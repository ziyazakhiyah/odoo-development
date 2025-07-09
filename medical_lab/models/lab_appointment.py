# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.addons.base.models.res_users import check_identity


class LabAppointment(models.Model):
    """
       Model for managing lab appointments.This class defines the structure a
       nd behavior of lab appointments, including the creation of invoices and
       lab test requests.
    """
    _name = 'lab.appointment'
    _inherit = ['mail.thread']
    _description = "Appointment"
    _order = 'appointment_date'

    user_id = fields.Many2one('res.users', help="Responsible user",
                              string='Responsible', readonly=True)
    patient_id = fields.Many2one('lab.patient',
                                 string='Patient', required=True,
                                 help='Patient Name')
    name = fields.Char(string='Appointment ID', readonly=True,
                       default=lambda self: _('New'),
                       help='Name of the lab appointment')
    date = fields.Datetime(string='Requested Date',
                           default=lambda s: fields.Datetime.now(),
                           help="Date in which patient appointment is noted")
    appointment_date = fields.Datetime(string='Appointment Date',
                                       default=lambda s: fields.Datetime.now(),
                                       help="This is the appointment date")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')
    ], default='0')

    stage_id = fields.Many2one('lab.stage', string='Status', required=True, group_expand="_read_group_expand_full")
    hospital_id = fields.Many2one(related='patient_id.hospital_id', string="Hospital")

    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
    )


    @api.depends('appointment_date')
    def _compute_is_overdue(self):
        today = datetime.date.today()
        for task in self:
            if task.appointment_date:
                task.is_overdue = task.appointment_date < today
            else:
                task.is_overdue = False


    @api.model_create_multi
    def create(self, vals_list):
        """
           Create a new lab appointment record.This method creates a new lab
           appointment record and assigns a unique appointment ID to it.
           :param self: The record itself.
           :param dict vals_list: A dictionary of values for creating the lab
           appointment record.
           :return: The created lab appointment record.
           :rtype: LabAppointment

        """
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'lab.appointment') or _('New')
        return super().create(vals_list)

    def action_done(self):
        self.stage_id = self.env.ref('medical_lab.stage_done').id
