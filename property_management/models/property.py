# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Property(models.Model):
    """Model containing details of property"""
    _name = 'property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Property Details'

    name = fields.Char(string="Property Name", required=True, tracking=True)
    city = fields.Char(string="City")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")
    property_image = fields.Image(string="Property")
    built_date = fields.Date(string="Built Date", tracking=True)
    can_be_sold = fields.Boolean(string="Can be sold", default=True, tracking=True)
    legal_amount = fields.Float(string="Legal Amount", tracking=True)
    rent = fields.Float(string="Rent", tracking=True)
    description = fields.Text(string="Description")
    owner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    state_property = fields.Selection(
        selection=[('draft', 'Draft'), ('rented', 'Rented'), ('leased', 'Leased'), ('sold', 'Sold')]
        , string='Status', tracking=True, default='draft')
    facilities_ids = fields.Many2many('facilities', string="Facilities")
    number_related_contracts = fields.Integer(compute='_compute_number_related_contracts')
    active = fields.Boolean(default=True)

    def _compute_number_related_contracts(self):
        """Compute the number of unique contracts linked to this property via rent.move.line."""
        RentLine = self.env['rent.move.line']
        for rec in self:
            rent_lines = RentLine.search([('property_id', '=', rec.id)])
            contract_ids = rent_lines.mapped('contract_id').ids
            rec.number_related_contracts = len(set(contract_ids))

    @api.onchange('state')
    def _onchange_state(self):
        """Function to check whether can_be_sold is True when state is changed to 'sold'"""
        if self.state == 'sold' and not self.can_be_sold:
            raise ValidationError("You can only set status to Sold if 'Can be Sold' is checked.")

    def unlink(self):
        """When a property is deleted, delete related contracts only if
        this is the only linked property, and also delete their invoices."""
        RentLine = self.env['rent.move.line']
        AccountMove = self.env['account.move']

        for property_rec in self:
            rent_lines = RentLine.search([('property_id', '=', property_rec.id)])
            related_contracts = rent_lines.mapped('contract_id')

            for contract in related_contracts:
                all_lines = RentLine.search([('contract_id', '=', contract.id)])
                linked_property_ids = all_lines.mapped('property_id.id')
                if linked_property_ids == [property_rec.id]:
                    invoices = AccountMove.search([('contract_id', '=', contract.id)])
                    invoices.unlink()
                    contract.unlink()

        return super().unlink()

    def action_open_rental_contracts(self):
        """Button to view related rental contracts via rent.move.line."""
        self.ensure_one()
        rent_lines = self.env['rent.move.line'].search([('property_id', '=', self.id)])
        contract_ids = rent_lines.mapped('contract_id').ids

        return {
            'type': 'ir.actions.act_window',
            'name': "Rental Contracts",
            'res_model': 'contract',
            'domain': [('id', 'in', contract_ids)],
            'view_mode': 'list,form',
        }
