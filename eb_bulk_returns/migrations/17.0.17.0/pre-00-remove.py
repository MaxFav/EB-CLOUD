from odoo.upgrade import util

def migrate(cr,version):
    util.remove_model(cr,"x_store")
    util.remove_model(cr,"smart_mtd.general_settings")
    util.remove_model(cr,"smart_mtd.fuel.scale.wizard")
    util.remove_model(cr,"smart_mtd.bad.debt.wizard")
    util.remove_module(cr,"smart_mtd")
    