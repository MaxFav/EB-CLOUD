from odoo.upgrade import util

def migrate(cr,version):
    util.remove_record(cr,"studio_customization.default_search_view__0bc837d7-719c-4759-a166-97a915f9e43f")