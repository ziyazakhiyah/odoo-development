# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Contract(models.Model):
    """Model containing contract details"""

    _name = 'contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', "portal.mixin"]
    _description = 'Renting and Leasing Contract'
    _rec_name = "reference"

    reference = fields.Char(string="Reference", default="New")
    property_ids = fields.Many2many('property', string="Name of Property", tracking=True, required=True)
    property_line_ids = fields.One2many('rent.move.line', 'contract_id', string="Properties")
    type = fields.Selection(string="Type of Contract", selection=[('rent', 'Rent'), ('lease', 'Lease')], tracking=True,
                            required=True)
    tenant_id = fields.Many2one('res.partner', string='Tenant', tracking=True, required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    total_days = fields.Integer(string="Total Days", compute="_compute_total_days")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('confirmed', 'Confirmed'), ('closed', 'Closed'),
                   ('returned', 'Returned'),
                   ('expired', 'Expired')]
        , string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    invoice_ids = fields.One2many('account.move', 'contract_id', string="Invoice")
    number_related_invoices = fields.Integer(compute='_compute_number_related_invoices')
    payment_state = fields.Selection(
        [('not_paid', 'Not Paid'), ('partial', 'Partially Paid'), ('in_payment', 'In Payment'), ('paid', 'Paid'),
         ], string="Payment Status", compute="_compute_payment_state")
    note = fields.Text()

    @api.depends('invoice_ids.payment_state')
    def _compute_payment_state(self):
        """Function to compute payment state of contract"""
        for contract in self:
            states = contract.invoice_ids.mapped('payment_state')
            if not states:
                contract.payment_state = 'not_paid'
            elif all(state == 'paid' for state in states):
                contract.payment_state = 'paid'
            elif any(state == 'in_payment' for state in states):
                contract.payment_state = 'in_payment'
            elif any(state == 'paid' for state in states):
                contract.payment_state = 'partial'
            else:
                contract.payment_state = 'not_paid'

    def _compute_number_related_invoices(self):
        """Function to show total related number of invoices"""
        for rec in self:
            rec.number_related_invoices = self.env['account.move'].search_count([('contract_id', '=', rec.id)])

    @api.depends('start_date', 'end_date')
    def _compute_total_days(self):
        """Function to calculate total days"""
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.total_days = (rec.end_date - rec.start_date).days + 1
            else:
                rec.total_days = 0

    @api.depends('property_line_ids.subtotal')
    def _compute_total_amount(self):
        """Function to calculate total amount"""
        for contract in self:
            contract.total_amount = sum(contract.property_line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        """Function to create sequence number"""
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == "New":
                vals['reference'] = self.env['ir.sequence'].next_by_code('contract')
        return super().create(vals_list)

    def action_confirm(self):
        """Function to change state to 'Confirmed' on the click of a button"""
        if self.message_attachment_count == 0:
            raise ValidationError("Missing Documents")
        else:
            if self.env.user.has_group('property_management.group_property_management_manager'):
                self.state = 'confirmed'
                for record in self:
                    for line in record.property_line_ids:
                        if record.type == 'rent':
                            line.property_id.state_property = 'rented'
                        elif record.type == 'lease':
                            line.property_id.state_property = 'leased'
                template = self.env.ref('property_management.contract_confirmation_email_template')
                template.send_mail(self.id, force_send=True)
            else:
                self.state = 'to_approve'

    def action_approve(self):
        self.action_confirm()

    def action_close(self):
        """Function to change state to 'Closed' on the click of a button"""
        self.state = 'closed'
        template = self.env.ref('property_management.contract_closing_email_template')
        template.send_mail(self.id, force_send=True)

    def action_return(self):
        """Function to change state to 'Returned' on the click of a button"""
        self.state = 'returned'

    def action_expired(self):
        """Function to change state to 'Expired' on the click of a button"""
        self.state = 'expired'
        template = self.env.ref('property_management.contract_expiry_email_template')
        template.send_mail(self.id, force_send=True)

    def action_draft(self):
        """Function to change state to 'Draft' on the click of a button"""
        self.state = 'draft'

    def action_open_related_invoices(self):
        """Button to view related invoices"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Invoices",
            'res_model': 'account.move',
            'domain': [('contract_id', '=', self.id)],
            'view_mode': 'list,form',
        }

    def action_create_draft_invoice(self):
        """Function to create invoice"""
        invoice_lines = []
        invoice_lines_all = self.invoice_ids.filtered(lambda inv: inv.state == 'posted').mapped('invoice_line_ids')

        invoiced_qty_by_line = {}
        for line in invoice_lines_all:
            invoiced_qty_by_line[line.property_line_id.id] = invoiced_qty_by_line.get(line.property_line_id.id,
                                                                                      0) + line.quantity

        for line in self.property_line_ids:
            total_qty = line.contract_id.total_days or 1
            invoiced_qty = invoiced_qty_by_line.get(line.id, 0)
            remaining_qty = total_qty - invoiced_qty

            if remaining_qty > 0:
                invoice_lines.append((0, 0, {
                    'name': line.property_id.name,
                    'quantity': remaining_qty,
                    'price_unit': line.price or 0.0,
                    'property_line_id': line.id,
                }))

        if not invoice_lines:
            raise ValidationError("All property lines are already fully invoiced.")

        existing_invoice = self.env['account.move'].search([
            ('contract_id', '=', self.id),
            ('state', '=', 'draft'),
            ('move_type', '=', 'out_invoice'),
        ], limit=1)

        if existing_invoice:
            existing_invoice.invoice_line_ids.unlink()
            existing_invoice.write({
                'invoice_line_ids': invoice_lines
            })
            return existing_invoice

        return self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.tenant_id.id,
            'contract_id': self.id,
            'invoice_line_ids': invoice_lines,
        })

    @api.model
    def check_and_mark_expired(self):
        """Function to check if contract is expired"""
        today = fields.Date.today()
        expired_records = self.search([('end_date', '<=', today)])
        for rec in expired_records:
            rec.action_expired()

    @api.model
    def reminder_payment_due(self):
        """Function to send email when payment is overdue"""
        expired_records = self.search([('state', '=', 'expired'), ('payment_state', '=', 'not_paid')])
        template = self.env.ref('property_management.payment_due_email_template')
        for rec in expired_records:
            template.send_mail(rec.id, force_send=True)

    def get_portal_url(self, suffix=None, report_type=None, download=False):
        self.ensure_one()
        url = f"/my/contracts/{self.id}"
        if suffix:
            url += f"/{suffix}"
        if report_type:
            url += f"?report_type={report_type}"
            if download:
                url += "&download=true"
        return url
