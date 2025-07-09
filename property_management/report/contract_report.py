# -- coding: utf-8 --
from odoo import models


class ContractReportAbstract(models.AbstractModel):
    _name = 'report.property_management.contract_report_template'
    _description = 'Contract Report Abstract'

    def _get_report_values(self, docids, data=None):

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        state = data.get('state')
        tenant_id = data.get('tenant_id', [])
        contract_type = data.get('type')
        owner_id = data.get('owner_id', [])
        property_id = data.get('property_id', [])

        query = """
            SELECT *
            FROM contract c
            LEFT JOIN rent_move_line rml ON rml.contract_id = c.id
            LEFT JOIN property p ON rml.property_id = p.id
            WHERE 1=1
        """

        if start_date:
            query += f" AND c.start_date >= '{start_date}'"
        if end_date:
            query += f" AND c.end_date <= '{end_date}'"
        if state:
            query += f" AND c.state = '{state}'"
        if tenant_id:
            query += f" AND c.tenant_id = '{tenant_id[0]}'"
        if contract_type:
            query += f" AND c.type = '{contract_type}'"
        if owner_id:
            query += f" AND p.owner_id = '{owner_id[0]}'"
        if property_id:
            query += f" AND rml.property_id = '{property_id[0]}'"

        self.env.cr.execute(query)
        contracts = self.env.cr.dictfetchall()

        state_selection = dict(self.env['contract'].fields_get(['state'])['state']['selection'])
        type_selection = dict(self.env['contract'].fields_get(['type'])['type']['selection'])

        for contract in contracts:
            tenant = self.env['res.partner'].browse(contract.get('tenant_id'))
            contract['tenant_name'] = tenant.name if tenant.exists() else ''
            prop = self.env['property'].browse(contract.get('property_id'))
            contract['property_name'] = prop.name if prop.exists() else ''
            contract['property_owner'] = prop.owner_id.name if prop.exists() else ''
            contract['start_date'] = contract.get('start_date') and str(contract['start_date'])
            contract['end_date'] = contract.get('end_date') and str(contract['end_date'])
            contract['state_label'] = state_selection.get(contract.get('state'))
            contract['type_label'] = type_selection.get(contract.get('type'))

        form = data.copy()
        form['state_label'] = state_selection.get(state) if state else ''
        form['type_label'] = type_selection.get(contract_type) if contract_type else ''

        return {
            'doc_ids': docids,
            'doc_model': 'contract.generate.report',
            'form': form,
            'contracts': contracts,
        }
