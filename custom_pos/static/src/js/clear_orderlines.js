/**@odoo-module **/
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ControlButtons.prototype, {
    setup() {
       super.setup();
       this.notification = useService("notification");
       this.dialog = useService("dialog");
       this.pos = usePos();
    },
    async onClickPopup() {
        await this.dialog.add(ConfirmationDialog, {
            body: _t("Are you sure you want to clear all orderlines?"),
            confirmClass: "btn-primary",
            confirmLabel: _t("Confirm"),
            confirm: () => {
                const order = this.pos.get_order();
                const lines = [...order.get_orderlines()];
                lines.forEach((line) => order.removeOrderline(line));
                this.notification.add(_t("Confirmed"), {
                    type: "success",
                });
            },
            cancelLabel: _t("Cancel"),
            cancel: () => { },
                });
    },
});

patch(Orderline.prototype, {
    setup() {
       super.setup();
       this.pos = usePos();
       this.numberBuffer = useService("number_buffer");
    },
    async onClickRemove() {
        this.numberBuffer.sendKey("Backspace");
        this.numberBuffer.sendKey("Backspace");
    },
});
