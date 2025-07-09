# -*- coding: utf-8 -*-
import io
import json
import xlsxwriter
import base64
from bs4 import BeautifulSoup
from odoo.tools import json_default
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ContractReport(models.TransientModel):
    """Wizard for generating Rent/Lease Contract Reports"""

    _name = 'contract.generate.report'
    _description = 'Rent/Lease Contract Report Wizard'

    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('to_approve', 'To Approve'), ('confirmed', 'Confirmed'), ('closed', 'Closed'),
                   ('returned', 'Returned'),
                   ('expired', 'Expired')], string='Status')
    owner_id = fields.Many2one('res.partner', string="Owner")
    tenant_id = fields.Many2one('res.partner', string='Tenant')
    property_id = fields.Many2one('property', string="Property")
    type = fields.Selection(string="Type of Contract", selection=[('rent', 'Rent'), ('lease', 'Lease')])

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validation for date range"""
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date < rec.start_date:
                    raise ValidationError("Invalid date range")

    def action_print_report(self):
        """Button to print PDF Report"""
        return self.env.ref('property_management.contract_report_action').report_action(
            self, data={
                'start_date': self.start_date,
                'end_date': self.end_date,
                'state': self.state,
                'tenant_id': [self.tenant_id.id, self.tenant_id.name] if self.tenant_id else None,
                'type': self.type,
                'owner_id': [self.owner_id.id, self.owner_id.name] if self.owner_id else None,
                'property_id': [self.property_id.id, self.property_id.name] if self.property_id else None,
            }
        )

    def action_print_report_xlsx(self):
        """Button to print Excel Report"""
        data = {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'state': self.state,
            'tenant_id': [self.tenant_id.id, self.tenant_id.name] if self.tenant_id else None,
            'type': self.type,
            'owner_id': [self.owner_id.id, self.owner_id.name] if self.owner_id else None,
            'property_id': [self.property_id.id, self.property_id.name] if self.property_id else None,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'contract.generate.report',
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Rent/Lease Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        """Function to create Excel Report"""
        report_model = self.env['report.property_management.contract_report_template']
        report_data = report_model._get_report_values(docids=[], data=data)
        contracts = report_data['contracts']
        form = report_data['form']

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Contract Report")

        heading_format = workbook.add_format({
            'bold': True, 'font_size': 22, 'align': 'center'
        })
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#D3D3D3', 'align': 'center'
        })
        content_format = workbook.add_format({'align': 'left'})
        filter_label_format = workbook.add_format({'bold': True, 'align': 'left'})

        company = self.env.company
        if company.logo:
            logo_data = base64.b64decode(company.logo)

            logo_image = io.BytesIO(logo_data)
            sheet.insert_image('H1', 'logo.png', {
                'image_data': logo_image,
                'x_offset': 2,
                'y_offset': 2,
                'x_scale': 0.3,
                'y_scale': 0.3
            })

        address_html = company.company_details or ''
        soup = BeautifulSoup(address_html, 'html.parser')
        address_lines = soup.get_text().strip()

        address_format = workbook.add_format({
            'align': 'left',
            'valign': 'top'
        })
        sheet.merge_range('H4:I7', address_lines, address_format)

        sheet.merge_range('A8:I10', 'Rent/Lease Report', heading_format)

        filters = []
        if form.get('start_date'):
            filters.append(('Start Date', str(form['start_date'])))
        if form.get('end_date'):
            filters.append(('End Date', str(form['end_date'])))
        if form.get('tenant_id'):
            filters.append(('Tenant', form['tenant_id'][1]))
        if form.get('owner_id'):
            filters.append(('Owner', form['owner_id'][1]))
        if form.get('property_id'):
            filters.append(('Property', form['property_id'][1]))
        if form.get('type_label'):
            filters.append(('Type', form['type_label']))
        if form.get('state_label'):
            filters.append(('State', form['state_label']))

        row = 11
        col = 0

        for label, value in filters:
            cell_text = f"{label}: {value}"
            sheet.merge_range(row, col, row, col + 1, cell_text, filter_label_format)
            col += 2

        sheet.set_column('A:A', 15)
        sheet.set_column('B:D', 25)
        sheet.set_column('E:I', 15)

        headers = [
            'Reference', 'Tenant', 'Property', 'Owner',
            'Type', 'From Date', 'To Date', 'Total Amount', 'State'
        ]
        for col_num, header in enumerate(headers):
            sheet.write(13, col_num, header, header_format)

        for row, record in enumerate(contracts, start=14):
            sheet.write(row, 0, record.get('reference') or '', content_format)
            sheet.write(row, 1, record.get('tenant_name') or '', content_format)
            sheet.write(row, 2, record.get('property_name') or '', content_format)
            sheet.write(row, 3, record.get('property_owner') or '', content_format)
            sheet.write(row, 4, record.get('type_label') or '', content_format)
            sheet.write(row, 5, str(record.get('start_date') or ''), content_format)
            sheet.write(row, 6, str(record.get('end_date') or ''), content_format)
            sheet.write_number(row, 7, record.get('total_amount') or '')
            sheet.write(row, 8, record.get('state_label') or '', content_format)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
