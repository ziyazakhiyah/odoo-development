/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";
import { loadJS } from "@web/core/assets";


class SalesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.charts = {};
        this.state = useState({
            data: {},
            filters: {
                team_filter: "this_month",
                person_filter: "this_month",
                product_filter: "this_month",
                low_product_filter: "this_month",
                customer_filter: "this_month",
                order_filter: "this_month",
                invoice_filter: "this_month",
                product_category_id: null,
                low_product_category_id: null,
            },
        });
        onMounted(() => this.load());
    }
    async load() {
        await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
        await this._fetch_data();
    }

    async _fetch_data() {
        const result = await this.orm.call("sale.order", "get_sales_dashboard_data", [], {
            context: this.state.filters,
        });
        this.state.data = result;
        this._render_charts();
    }

    goToRecord(model, id) {
        window.location.href = `/web#model=${model}&id=${id}&view_type=form`;
    }

    _render_charts() {
        const d = this.state.data;
        if (!d.sales_by_team) return;
        Object.values(this.charts).forEach(chart => chart?.destroy());
        this.charts = {};

        const pie = (id, labels, data, bg, chartKey) => {
            const ctx = document.getElementById(id);
            if (!ctx) return;
            this.charts[chartKey] = new Chart(ctx, {
                type: "pie",
                data: {
                    labels,
                    datasets: [{ data, backgroundColor: bg }],
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        };
        const bar = (id, labels, data, bg, chartKey) => {
            const ctx = document.getElementById(id);
            if (!ctx) return;
            this.charts[chartKey] = new Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [{ label: "", data, backgroundColor: bg }],
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true } },
                    plugins: { legend: { display: false } }
                }
            });
        };

        pie("salesByTeamChart",
            d.sales_by_team.map(x => x.name),
            d.sales_by_team.map(x => x.amount),
            ["#007bff", "#28a745", "#ffc107", "#dc3545", "#ff7e00"],
            "team");

        pie("salesByPersonChart",
            d.sales_by_person.map(x => x.name),
            d.sales_by_person.map(x => x.amount),
            ["#17a2b8", "#ffc107", "#6c757d", "#6610f2"],
            "person");

        bar("topProductsChart",
            d.top_products.map(x => x.name),
            d.top_products.map(x => x.qty),
            "#28a745",
            "top_products");

        bar("lowestProductsChart",
            d.lowest_products.map(x => x.name),
            d.lowest_products.map(x => x.qty),
            "#dc3545",
            "lowest_products");

        pie("orderStatusChart",
            d.order_status.map(x => x.status),
            d.order_status.map(x => x.count),
            ["#6c757d", "#17a2b8", "#28a745", "#ffc107"],
            "order_status");

        pie("invoiceStatusChart",
            d.invoice_status.map(x => x.status),
            d.invoice_status.map(x => x.count),
            ["#343a40", "#28a745", "#ffc107"],
            "invoice_status");
    }

    // Filter handlers
    onChangeTeamFilter(ev) {
        this.state.filters.team_filter = ev.target.value;
        this._fetch_data();
    }
    onChangePersonFilter(ev) {
        this.state.filters.person_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeCustomerFilter(ev) {
        this.state.filters.customer_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeOrderFilter(ev) {
        this.state.filters.order_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeInvoiceFilter(ev) {
        this.state.filters.invoice_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeProductFilter(ev) {
        this.state.filters.product_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeProductCategory(ev) {
        const val = ev.target.value;
        this.state.filters.product_category_id = val ? parseInt(val) : null;
        this._fetch_data();
    }
    onChangeLowProductFilter(ev) {
        this.state.filters.low_product_filter = ev.target.value;
        this._fetch_data();
    }
    onChangeLowProductCategory(ev) {
        const val = ev.target.value;
        this.state.filters.low_product_category_id = val ? parseInt(val) : null;
        this._fetch_data();
    }
}
SalesDashboard.template = "sales_dashboard.SalesDashboardTemplate";
registry.category("actions").add("sales_dashboard", SalesDashboard);