/** @odoo-module **/

import { Order,Orderline,Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Payment.prototype, {
    setup() {
        super.setup(...arguments);       
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.sh_analytic_account = this.pos.config.sh_analytic_account[0] || null;
        return json;
    },
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.sh_pos_order_analytic_account = this.pos.config.sh_analytic_account[0] || null;
        return json;
    },
});

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.sh_pos_order_analytic_account = this.pos.config.sh_analytic_account[0] || null;
        return json;
    }
});
