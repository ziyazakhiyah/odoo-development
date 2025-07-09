/** @odoo-module **/
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline.prototype, {
    getDisplayData() {
        const data = super.getDisplayData() || {};
        const product = this.get_product();

        const brand = product?.brand_id;
        const formattedBrand = (brand && typeof brand === "object" && brand.id && brand.name)
            ? [brand.id, brand.name]
            : false;

        return {
            ...data,
            brand_id: formattedBrand,
        };
    },
});

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                brand_id: { type: [Array, Boolean], optional: true },
            },
        },
    },
});