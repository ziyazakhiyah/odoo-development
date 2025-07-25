# -*- coding: utf-8 -*-
import base64
from datetime import timedelta
from odoo import fields, models, api


class SalesReportManager(models.Model):
    _name = 'sales.report.manager'

    def F(self, partner, order_ids, report_date, date_from, date_to, frequency,
                                 sales_team_name=None):
        if not order_ids:
            return
        orders = self.env['sale.order'].browse(order_ids)
        complete_orders_data = []
        for order in orders:
            complete_orders_data.append({
                'id': order.id,
                'name': order.name,
                'date_order': order.date_order,
                'amount_total': order.amount_total,
                'sales_team': order.team_id.name,
                'order_line': [{
                    'product': line.product_id.display_name,
                    'qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'subtotal': line.price_subtotal,
                } for line in order.order_line],
            })
        pdf = self.env['ir.actions.report']._render_qweb_pdf(
            'monthly_weekly_sales_report.action_sales_summary_pdf',
            res_ids=orders.ids,
            data={
                'orders': complete_orders_data,
                'partner': partner,
                'report_date': report_date,
                'date_from': date_from,
                'date_to': date_to,
                'sales_team': sales_team_name or ""
            }
        )[0]
        attachment = self.env['ir.attachment'].create({
            'name': f"{frequency.capitalize()}_Sales_Report_{partner.name}_{sales_team_name or ""}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'res_model': 'res.partner',
            'res_id': partner.id,
            'mimetype': 'application/pdf',
        })
        return attachment

    @api.model
    def _send_sales_report(self, frequency):
        param = self.env['ir.config_parameter'].sudo()
        configured_frequency = param.get_param('monthly_weekly_sales_report.frequency')
        if configured_frequency != frequency:
            return
        sales_team_ids_str = param.get_param('monthly_weekly_sales_report.sales_team_ids', '')
        sales_team_ids = [int(x) for x in sales_team_ids_str.split(',') if x]
        selected_teams = self.env['crm.team'].browse(sales_team_ids)
        customer_ids_str = param.get_param('monthly_weekly_sales_report.customer_ids', '')
        if customer_ids_str:
            customer_ids = [int(x) for x in customer_ids_str.split(',') if x]
            customers = self.env['res.partner'].browse(customer_ids)
        else:
            customers = self.env['res.partner'].search([])
        today = fields.Date.today()
        start_date_str = param.get_param('monthly_weekly_sales_report.from_date')
        end_date_str = param.get_param('monthly_weekly_sales_report.to_date')
        if start_date_str and end_date_str:
            date_from = fields.Date.from_string(start_date_str)
            date_to = fields.Date.from_string(end_date_str)
        else:
            date_from = today.replace(day=1) if frequency == 'monthly' else today - timedelta(days=7)
            date_to = today
        for partner in customers:
            attachments = []
            if selected_teams:
                for team in selected_teams:
                    query = """
                        SELECT so.id
                        FROM sale_order so
                        WHERE so.partner_id = %s
                          AND so.state IN ('sale')
                          AND so.date_order >= %s
                          AND so.date_order <= %s
                          AND so.team_id = %s
                    """
                    self.env.cr.execute(query, (partner.id, date_from, date_to, team.id))
                    order_ids = [row['id'] for row in self.env.cr.dictfetchall()]
                    if order_ids:
                        attachment = self._generate_pdf_attachment(
                            partner, order_ids, today, date_from, date_to, frequency, team.name
                        )
                        attachments.append(attachment.id)
            else:
                query = """
                    SELECT so.id
                    FROM sale_order so
                    WHERE so.partner_id = %s
                      AND so.state IN ('sale')
                      AND so.date_order >= %s
                      AND so.date_order <= %s
                """
                self.env.cr.execute(query, (partner.id, date_from, date_to))
                order_ids = [row['id'] for row in self.env.cr.dictfetchall()]
                if order_ids:
                    attachment = self._generate_pdf_attachment(
                        partner, order_ids, today, date_from, date_to, frequency
                    )
                    attachments.append(attachment.id)
            if attachments:
                template_id = (
                    'monthly_weekly_sales_report.monthly_sales_report_email_template'
                    if frequency == 'monthly'
                    else 'monthly_weekly_sales_report.weekly_sales_report_email_template'
                )
                template = self.env.ref(template_id)
                template.send_mail(partner.id, force_send=True, email_values={
                    'email_to': partner.email,
                    'attachment_ids': attachments,
                })
