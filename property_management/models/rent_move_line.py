# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RentMoveLine(models.Model):
    """Model for lines"""
    _name = 'rent.move.line'
    _rec_name = 'property_id'

    property_id = fields.Many2one('property', string='Property', domain=[('state_property', '=', 'draft')])
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal")
    contract_id = fields.Many2one('contract', string="Contract")
    price = fields.Float(string="Price", compute="_compute_price", inverse="_inverse_price")
    qty = fields.Integer(string="Quantity", related="contract_id.total_days")
    invoice_line_ids = fields.One2many('account.move.line', 'property_line_id',
                                       string="Invoice Lines")
    invoiced_qty = fields.Float("Invoiced Quantity", compute="_compute_invoiced_qty")

    @api.depends('invoice_line_ids.quantity')
    def _compute_invoiced_qty(self):
        """Function to compute invoiced quantities"""
        for line in self:
            line.invoiced_qty = sum(l.quantity for l in line.invoice_line_ids)

    @api.depends('property_id', 'contract_id.type')
    def _compute_price(self):
        """Function to get the rent or legal amount of each property"""
        for line in self:
            if line.contract_id.type == 'rent':
                line.price = line.property_id.rent
            else:
                line.price = line.property_id.legal_amount

    def _inverse_price(self):
        """Function to edit default price of property"""
        for line in self:
            if line.contract_id.type == 'rent':
                line.property_id.rent = line.price
            else:
                line.property_id.legal_amount = line.price

    @api.depends('property_id', 'contract_id.start_date', 'contract_id.end_date', 'contract_id.type')
    def _compute_subtotal(self):
        """Function to calculate subtotal of each property"""
        for line in self:
            subtotal = 0.0
            if line.contract_id and line.property_id:
                total_days = line.contract_id.total_days
                if line.contract_id.type == 'rent':
                    rent = line.property_id.rent
                    subtotal = total_days * rent
                elif line.contract_id.type == 'lease':
                    legal_amount = line.property_id.legal_amount
                    subtotal = total_days * legal_amount
            line.subtotal = subtotal
