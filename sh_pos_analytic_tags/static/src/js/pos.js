odoo.define('sh_pos_analytic.pos', function (require) {
    'use strict';

    var models = require('point_of_sale.models')

    models.load_fields('pos.session', ['sh_analytic_account', 'sh_analytic_tags'])

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var self = this;
            var result = _super_Order.export_as_JSON.call(this, arguments)
            if (self.pos && self.pos.pos_session && self.pos.pos_session.sh_analytic_account) {
                result['sh_pos_order_analytic_account'] = self.pos.pos_session.sh_analytic_account[0]
            }
            if (self.pos && self.pos.pos_session && self.pos.pos_session.sh_analytic_tags) {
                result['sh_pos_order_analytic_account_tags'] = self.pos.pos_session.sh_analytic_tags
            }
            return result
        }
    })
    var _super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function () {
            var self = this;
            var result = _super_Orderline.export_as_JSON.call(this, arguments)
            if (self.pos && self.pos.pos_session && self.pos.pos_session.sh_analytic_account) {
                result['sh_pos_order_analytic_account'] = self.pos.pos_session.sh_analytic_account[0]
            }
            if (self.pos && self.pos.pos_session && self.pos.pos_session.sh_analytic_tags) {
                result['sh_pos_order_analytic_account_tags'] = self.pos.pos_session.sh_analytic_tags
            }
            return result
        }
    })

    var _super_Paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        export_as_JSON: function () {
            var res = _super_Paymentline.export_as_JSON.apply(this, arguments)
            if (self.posmodel && self.posmodel.pos_session && self.posmodel.pos_session.sh_analytic_account) {
                res['sh_analytic_account'] = self.posmodel.pos_session.sh_analytic_account[0]
                res['sh_analytic_tags'] = self.posmodel.pos_session.sh_analytic_tags
            }
            return res
        }
    });
});
