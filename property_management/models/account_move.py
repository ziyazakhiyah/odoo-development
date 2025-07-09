# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    """Inheriting account.move model for invoicing"""
    _inherit = 'account.move'

    contract_id = fields.Many2one('contract', string="Rent/Lease Contract")

    def write(self, vals):
        """Function to create invoice"""
        res = super().write(vals)
        self._update_invoiced_quantities()
        return res

    def action_post(self):
        """Function to log message in chatter when posting related invoices"""
        res = super().action_post()

        for move in self:
            if move.move_type == 'out_invoice':
                contracts = self.env['contract'].search([('invoice_ids', 'in', move.ids)])
                for contract in contracts:
                    contract.message_post(
                        body=f"Invoice {move.name} has been posted.",
                        subject="Invoice Posted"
                    )
        return res

    def _update_invoiced_quantities(self):
        """Function to update invoiced quantities"""
        invoices = self.filtered(
            lambda inv: inv.move_type == 'out_invoice' and inv.state in {'draft', 'posted'})
        for invoice in invoices:
            for line in invoice.invoice_line_ids.filtered(lambda l: l.property_line_id):
                line.property_line_id.invoiced_qty += line.quantity
