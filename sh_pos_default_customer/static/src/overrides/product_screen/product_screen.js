/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.pos.get_order();
        var self = this;
        var order = self.pos.get_order();
        if (!order.get_partner()) {
            if (self.pos.config.sh_enable_default_customer && self.pos.config.sh_default_customer_id) {
                var set_partner = self.pos.db.get_partner_by_id(self.pos.config.sh_default_customer_id[0]);
                if (set_partner) {
                    order.set_partner(set_partner);
                }
            } else if (self.pos && self.pos.get_order()) {
                self.pos.get_order().set_partner(null);
            }
        }
    },
});
