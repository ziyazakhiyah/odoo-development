# -*- coding: utf-8 -*-
from odoo import models, api
from datetime import date, timedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_range(self, filter_key):
        today = date.today()
        if filter_key == 'this_month':
            return today.replace(day=1), today
        elif filter_key == 'last_month':
            first = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last = today.replace(day=1) - timedelta(days=1)
            return first, last
        elif filter_key == 'this_year':
            return today.replace(month=1, day=1), today
        elif filter_key == 'last_quarter':
            current_month = today.month
            current_quarter = (current_month - 1) // 3 + 1
            start_month = 3 * (current_quarter - 2) + 1
            start_year = today.year if current_quarter > 1 else today.year - 1
            start = date(start_year, start_month, 1)
            end_month = start_month + 2
            end = date(start_year, end_month, 1).replace(day=1) + timedelta(days=31)
            end = end.replace(day=1) - timedelta(days=1)
            return start, end
        return None, None

    @api.model
    def get_sales_dashboard_data(self, filters=None):
        filters = filters or {}
        env = self.env
        # ---------- 1. Sales by Team ----------
        team_filter_key = filters.get("team_filter")
        from_date, to_date = self._get_range(team_filter_key)
        domain = [('state', 'in', ['sale', 'done'])]
        if from_date:
            domain.append(("date_order", ">=", from_date))
        if to_date:
            domain.append(("date_order", "<=", to_date))
        if filters.get("team_id"):
            domain.append(("team_id", "=", int(filters["team_id"])))
        sales_team_data = env['sale.order'].read_group(domain, ['amount_total'], ['team_id'])
        teams = [
            {
                'id': t['team_id'][0],
                'name': t['team_id'][1],
                'amount': t['amount_total']
            }
            for t in sales_team_data if t['team_id']
        ]
        # ---------- 2. Sales by Salesperson ----------
        person_filter_key = filters.get("person_filter", "this_month")
        from_date, to_date = self._get_range(person_filter_key)
        person_domain = [('state', 'in', ['sale', 'done'])]
        if from_date:
            person_domain.append(("date_order", ">=", from_date))
        if to_date:
            person_domain.append(("date_order", "<=", to_date))
        if filters.get("team_id"):
            person_domain.append(("team_id", "=", int(filters["team_id"])))
        salesperson_data = env['sale.order'].read_group(person_domain, ['amount_total'], ['user_id'])
        persons = [
            {
                'id': p['user_id'][0],
                'name': p['user_id'][1],
                'amount': p['amount_total']
            }
            for p in salesperson_data if p['user_id']
        ]
        # ---------- 3. Top Customers ----------
        customer_filter_key = filters.get("customer_filter", "this_month")
        from_date, to_date = self._get_range(customer_filter_key)
        cust_domain = [('state', 'in', ['sale', 'done'])]
        if from_date:
            cust_domain.append(("date_order", ">=", from_date))
        if to_date:
            cust_domain.append(("date_order", "<=", to_date))
        top_customers = env['sale.order'].read_group(cust_domain, ['amount_total'], ['partner_id'])
        top_customers = sorted(top_customers, key=lambda x: x['amount_total'], reverse=True)[:10]
        customers = [
            {
                'id': c['partner_id'][0],
                'name': c['partner_id'][1],
                'amount': c['amount_total']
            }
            for c in top_customers if c['partner_id']
        ]
        # ---------- 4. Top & Lowest Selling Products ----------
        product_filter_key = filters.get("product_filter", "this_month")
        from_date, to_date = self._get_range(product_filter_key)
        sale_line_domain = []
        if from_date:
            sale_line_domain.append(("order_id.date_order", ">=", from_date))
        if to_date:
            sale_line_domain.append(("order_id.date_order", "<=", to_date))
        if filters.get("team_id"):
            sale_line_domain.append(("order_id.team_id", "=", int(filters["team_id"])))
        if filters.get("product_category_id"):
            sale_line_domain.append(("product_id.categ_id", "=", int(filters["product_category_id"])))
        top_products = env['sale.order.line'].read_group(sale_line_domain, ['product_id', 'product_uom_qty'], ['product_id'])
        top_products = sorted(top_products, key=lambda x: x['product_uom_qty'], reverse=True)[:10]
        top_products_list = [
            {
                'id': p['product_id'][0],
                'name': p['product_id'][1],
                'qty': p['product_uom_qty']
            }
            for p in top_products if p['product_id']
        ]
        low_product_filter_key = filters.get("low_product_filter", "this_month")
        from_date, to_date = self._get_range(low_product_filter_key)
        sale_line_domain_low = []
        if from_date:
            sale_line_domain_low.append(("order_id.date_order", ">=", from_date))
        if to_date:
            sale_line_domain_low.append(("order_id.date_order", "<=", to_date))
        if filters.get("team_id"):
            sale_line_domain_low.append(("order_id.team_id", "=", int(filters["team_id"])))
        if filters.get("low_product_category_id"):
            sale_line_domain_low.append(("product_id.categ_id", "=", int(filters["low_product_category_id"])))
        low_products = env['sale.order.line'].read_group(sale_line_domain_low, ['product_id', 'product_uom_qty'],
                                                         ['product_id'])
        low_products = sorted(low_products, key=lambda x: x['product_uom_qty'])[:10]
        low_products_list = [
            {
                'id': p['product_id'][0],
                'name': p['product_id'][1],
                'qty': p['product_uom_qty']
            }
            for p in low_products if p['product_id']
        ]
        # ---------- 5. Order Status ----------
        order_filter_key = filters.get("order_filter", "this_month")
        from_date, to_date = self._get_range(order_filter_key)
        order_domain = []
        if from_date:
            order_domain.append(("date_order", ">=", from_date))
        if to_date:
            order_domain.append(("date_order", "<=", to_date))
        ORDER_STATUS_LABELS = {
            'draft': 'Quotation',
            'sent': 'Quotation Sent',
            'sale': 'Sales Order',
            'done': 'Locked',
            'cancel': 'Cancelled'
        }
        orders = env['sale.order'].read_group(order_domain, fields=['state', 'id:count'], groupby=['state'], lazy=False)
        order_status = [
            {
                'status': ORDER_STATUS_LABELS.get(o['state'], o['state'].capitalize()),
                'count': o.get('__count', 0)
            } for o in orders
        ]
        # ---------- 6. Invoice Status ----------
        invoice_filter_key = filters.get("invoice_filter", "this_month")
        from_date, to_date = self._get_range(invoice_filter_key)
        invoice_domain = [('move_type', '=', 'out_invoice')]
        if from_date:
            invoice_domain.append(("invoice_date", ">=", from_date))
        if to_date:
            invoice_domain.append(("invoice_date", "<=", to_date))
        INVOICE_STATUS_LABELS = {
            'draft': 'Draft',
            'posted': 'Posted',
            'cancel': 'Cancelled'
        }
        invoices = env['account.move'].read_group(invoice_domain, fields=['state', 'id:count'], groupby=['state'], lazy=False)
        invoice_status = [
            {
                'status': INVOICE_STATUS_LABELS.get(i['state'], i['state'].capitalize()),
                'count': i.get('__count', 0)
            } for i in invoices
        ]
        return {
            'sales_by_team': teams,
            'sales_by_person': persons,
            'top_customers': customers,
            'top_products': top_products_list,
            'lowest_products': low_products_list,
            'order_status': order_status,
            'invoice_status': invoice_status,
            'team_options': [{'id': t.id, 'name': t.name} for t in env['crm.team'].search([])],
            'product_categories': [{'id': c.id, 'name': c.name} for c in env['product.category'].search([])],
        }
