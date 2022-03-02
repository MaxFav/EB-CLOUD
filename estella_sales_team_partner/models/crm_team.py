from odoo import api, fields, models, _

class CrmTeam(models.Model):
    _inherit = "crm.team"

    def _get_default_team_id(self, user_id=None, domain=None):
        if self.env.context.get('default_team_id'):
            return self.env['crm.team'].browse(self.env.context.get('default_team_id'))
        else:
            return super(CrmTeam, self)._get_default_team_id(user_id, domain)