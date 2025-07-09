/** @odoo-module */

import { renderToElement } from "@web/core/utils/render";
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

function chunkArray(arr, size) {
    const chunks = [];
    for (let i = 0; i < arr.length; i += size) {
        chunks.push(arr.slice(i, i + size));
    }
    return chunks;
}

publicWidget.registry.get_product_tab = publicWidget.Widget.extend({
    selector: '.properties_section',

    async willStart() {
        const result = await rpc('/get_properties', {});

        if (result && Array.isArray(result.properties) && result.properties.length) {
            const propertyChunks = chunkArray(result.properties, 4);
            propertyChunks[0].is_active = true;

            this.$target.empty().html(
                renderToElement('property_management.property_data', {
                    property_chunks: propertyChunks
                })
            );
        }
    },
});
