from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_assign():
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.move_ids.filtered(lambda move: move.state not in ('draft', 'cancel', 'done')).sorted(
            key=lambda move: (-int(move.priority), not bool(move.date_deadline), move.date_deadline, move.date, move.id)
        )
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        
        if self.env.context.get('set_quantity_done_from_cron'):
            moves.action_assign(force_qty=True)
            return super().action_assign()
        return super().action_assign()

