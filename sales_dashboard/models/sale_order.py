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
        cr = self.env.cr

        def date_condition(field, from_date, to_date):
            domain = ""
            params = []
            if from_date:
                domain += f" AND {field} >= %s"
                params.append(from_date)
            if to_date:
                domain += f" AND {field} <= %s"
                params.append(to_date)
            return domain, params

        # ---------- 1. Sales by Team ----------
        from_date, to_date = self._get_range(filters.get("team_filter"))
        domain, params = date_condition("date_order", from_date, to_date)
        team_id_filter = filters.get("team_id")
        if team_id_filter:
            domain += " AND team_id = %s"
            params.append(int(team_id_filter))

        cr.execute(f"""
            SELECT team_id, SUM(amount_total) as total
            FROM sale_order
            WHERE state IN ('sale', 'done') {domain}
            GROUP BY team_id
        """, params)
        teams = []
        for row in cr.fetchall():
            team = self.env['crm.team'].browse(row[0])
            teams.append({'id': team.id, 'name': team.name, 'amount': row[1]})

        # ---------- 2. Sales by Salesperson ----------
        from_date, to_date = self._get_range(filters.get("person_filter"))
        domain, params = date_condition("date_order", from_date, to_date)
        if team_id_filter:
            domain += " AND team_id = %s"
            params.append(int(team_id_filter))
        cr.execute(f"""
            SELECT user_id, SUM(amount_total) as total
            FROM sale_order
            WHERE state IN ('sale', 'done') {domain}
            GROUP BY user_id
        """, params)
        persons = []
        for row in cr.fetchall():
            user = self.env['res.users'].browse(row[0])
            persons.append({'id': user.id, 'name': user.name, 'amount': row[1]})

        # ---------- 3. Top Customers ----------
        from_date, to_date = self._get_range(filters.get("customer_filter"))
        domain, params = date_condition("date_order", from_date, to_date)
        cr.execute(f"""
            SELECT partner_id, SUM(amount_total) as total
            FROM sale_order
            WHERE state IN ('sale', 'done') {domain}
            GROUP BY partner_id
            ORDER BY total DESC
            LIMIT 10
        """, params)
        customers = []
        for row in cr.fetchall():
            partner = self.env['res.partner'].browse(row[0])
            customers.append({'id': partner.id, 'name': partner.name, 'amount': row[1]})

        # ---------- 4. Top Products ----------
        from_date, to_date = self._get_range(filters.get("product_filter"))
        domain, params = date_condition("so.date_order", from_date, to_date)
        product_cat_filter = filters.get("product_category_id")
        if product_cat_filter:
            domain += " AND p.categ_id = %s"
            params.append(int(product_cat_filter))
        if team_id_filter:
            domain += " AND so.team_id = %s"
            params.append(int(team_id_filter))
        cr.execute(f"""
            SELECT l.product_id, SUM(l.product_uom_qty) as total_qty
            FROM sale_order_line l
            JOIN sale_order so ON l.order_id = so.id
            JOIN product_product pr ON pr.id = l.product_id
            JOIN product_template p ON pr.product_tmpl_id = p.id
            WHERE 1=1 {domain}
            GROUP BY l.product_id
            ORDER BY total_qty DESC
            LIMIT 10
        """, params)
        top_products_list = []
        for row in cr.fetchall():
            prod = self.env['product.product'].browse(row[0])
            top_products_list.append({'id': prod.id, 'name': prod.name, 'qty': row[1]})

        # ---------- 5. Lowest Products ----------
        from_date, to_date = self._get_range(filters.get("low_product_filter"))
        domain, params = date_condition("so.date_order", from_date, to_date)
        low_product_cat_filter = filters.get("low_product_category_id")
        if low_product_cat_filter:
            domain += " AND p.categ_id = %s"
            params.append(int(low_product_cat_filter))
        if team_id_filter:
            domain += " AND so.team_id = %s"
            params.append(int(team_id_filter))
        cr.execute(f"""
            SELECT l.product_id, SUM(l.product_uom_qty) as total_qty
            FROM sale_order_line l
            JOIN sale_order so ON l.order_id = so.id
            JOIN product_product pr ON pr.id = l.product_id
            JOIN product_template p ON pr.product_tmpl_id = p.id
            WHERE 1=1 {domain}
            GROUP BY l.product_id
            ORDER BY total_qty ASC
            LIMIT 10
        """, params)
        low_products_list = []
        for row in cr.fetchall():
            prod = self.env['product.product'].browse(row[0])
            low_products_list.append({'id': prod.id, 'name': prod.name, 'qty': row[1]})

        # ---------- 6. Order Status ----------
        from_date, to_date = self._get_range(filters.get("order_filter"))
        domain, params = date_condition("date_order", from_date, to_date)
        cr.execute(f"""
            SELECT state, COUNT(id)
            FROM sale_order
            WHERE 1=1 {domain}
            GROUP BY state
        """, params)
        ORDER_STATUS_LABELS = {
            'draft': 'Quotation',
            'sent': 'Quotation Sent',
            'sale': 'Sales Order',
            'done': 'Locked',
            'cancel': 'Cancelled'
        }
        order_status = [
            {
                'status': ORDER_STATUS_LABELS.get(row[0], row[0].capitalize()),
                'count': row[1]
            } for row in cr.fetchall()
        ]

        # ---------- 7. Invoice Status ----------
        from_date, to_date = self._get_range(filters.get("invoice_filter"))
        domain, params = date_condition("invoice_date", from_date, to_date)
        cr.execute(f"""
            SELECT state, COUNT(id)
            FROM account_move
            WHERE move_type = 'out_invoice' {domain}
            GROUP BY state
        """, params)
        INVOICE_STATUS_LABELS = {
            'draft': 'Draft',
            'posted': 'Posted',
            'cancel': 'Cancelled'
        }
        invoice_status = [
            {
                'status': INVOICE_STATUS_LABELS.get(row[0], row[0].capitalize()),
                'count': row[1]
            } for row in cr.fetchall()
        ]

        return {
            'sales_by_team': teams,
            'sales_by_person': persons,
            'top_customers': customers,
            'top_products': top_products_list,
            'lowest_products': low_products_list,
            'order_status': order_status,
            'invoice_status': invoice_status,
            'team_options': [{'id': t.id, 'name': t.name} for t in self.env['crm.team'].search([])],
            'product_categories': [{'id': c.id, 'name': c.name} for c in self.env['product.category'].search([])],
        }
