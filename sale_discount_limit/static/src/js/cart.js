/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.websiteSaleCart.include({
    events: {
        'click .js_delete_cart': '_onClickDeleteCart',
    },

    _onClickDeleteCart: function (ev) {
        ev.preventDefault();
        rpc('/shop/clear_cart', {}).then(() => {
            window.location.reload();
        });
    }
});