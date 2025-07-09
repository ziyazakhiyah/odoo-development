# -*- coding: utf-8 -*-
import json
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http, fields
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class XLSXReportController(http.Controller):
    @http.route('/xlsx_reports', type='http', auth='user',
                csrf=False)
    def get_report_xlsx(self, model, options, output_format, report_name,
                        token='ads'):
        """ Return data to python file passed from the javascript"""
        session_unique_id = request.session.uid
        report_object = request.env[model].with_user(session_unique_id)
        options = json.loads(options)
        try:
            if output_format == 'xlsx':
                response = request.make_response(
                    None,
                    headers=[('Content-Type', 'application/vnd.ms-excel'), (
                        'Content-Disposition',
                        content_disposition(f"{report_name}.xlsx"))
                             ]
                )
                report_object.get_xlsx_report(options, response)
                response.set_cookie('fileToken', token)
                return response
        except Exception:
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
            }
            return request.make_response(html_escape(json.dumps(error)))


class ContractController(http.Controller):
    @http.route('/contract_webform', type='http', auth='user', website=True)
    def contract_webform(self):
        """Fetch data from db and send it to the form"""
        user = request.env.user
        if not (user.has_group('base.group_portal') or user.has_group('base.group_system')):
            raise AccessDenied()

        properties = request.env['property'].search([])
        tenants = request.env['res.partner'].search([])

        property_data = {
            prop.id: {
                'rent': prop.rent,
                'legal_amount': prop.legal_amount,
            } for prop in properties
        }

        property_data_json = json.dumps(property_data)

        return request.render('property_management.create_contract', {
            'properties': properties,
            'tenants': tenants,
            'property_data_json': property_data_json,
        })

    @http.route('/create/webcontract', type="http", auth="user", website=True)
    def create_webcontract(self, **post):
        """Action to create record in backend"""
        tenant_id = int(post.get('tenant_id', 0))
        index = 0
        property_line_vals = []
        while True:
            prop_id = post.get(f'property_id_{index}')
            qty = post.get(f'qty_{index}')
            price = post.get(f'price_{index}')
            if not prop_id:
                break

            property_line_vals.append(fields.Command.create({
                'property_id': int(prop_id),
                'qty': int(qty) if qty else 1,
                'price': float(price) if price else 0.0,
            }))
            index += 1

        request.env['contract'].create({
            'type': post.get('type'),
            'tenant_id': tenant_id,
            'start_date': post.get('start_date'),
            'end_date': post.get('end_date'),
            'note': post.get('note'),
            'property_line_ids': property_line_vals,
        })

        return request.render("property_management.contract_thanks", {})

    @http.route('/my/contracts', type='http', auth='user', website=True)
    def portal_my_contracts(self):
        contracts = request.env['contract'].search([])
        return request.render("property_management.portal_contracts", {
            'contracts': contracts,
        })


class ContractPortal(CustomerPortal):
    @http.route(['/my/contracts/<int:contract_id>'], type='http', auth='public', website=True)
    def portal_contract_page(self, contract_id, access_token=None):
        try:
            contract_sudo = self._document_check_access('contract', contract_id, access_token=access_token)
        except (AccessError):
            return request.redirect('/my/contracts')

        state_selection = dict(contract_sudo._fields['state'].selection)
        type_selection = dict(contract_sudo._fields['type'].selection)

        values = {
            'contract': contract_sudo,
            'res_company': contract_sudo.company_id,
            'access_token': access_token,
            'state_label': state_selection.get(contract_sudo.state, ''),
            'type_label': type_selection.get(contract_sudo.type, ''),
        }

        return request.render("property_management.portal_contract_page", values)


class WebsiteSnippet(http.Controller):
    @http.route('/properties', auth="public", type='http', website=True)
    def properties(self):
        return request.render("property_management.property_page")

    @http.route('/get_properties', auth="public", type='json', website=True)
    def get_properties(self):
        """Return property data in JSON format for JS rendering."""
        Property = request.env['property']
        properties = Property.search_read([], ['name', 'property_image', 'state_property', 'rent', 'legal_amount'],
                                          order='create_date desc')
        selection = dict(Property.fields_get(['state_property'])['state_property']['selection'])
        for prop in properties:
            state_value = prop.get('state_property')
            prop['state'] = selection.get(state_value, '')
        return {
            'properties': properties
        }

    @http.route('/property/<int:property_id>', auth='public', website=True)
    def property_detail(self, property_id):
        property = request.env['property'].browse(property_id)
        if not property.exists():
            return request.not_found()
        image_base64 = property.property_image.decode('utf-8') if property.property_image else None
        status_selection = dict(
            request.env['property'].fields_get(allfields=['state_property'])['state_property']['selection'])
        state = status_selection.get(property.state_property)

        return request.render('property_management.property_detail_page', {
            'property': property,
            'image_base64': image_base64,
            'state': state,
        })
