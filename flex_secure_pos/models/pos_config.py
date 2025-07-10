# -*- coding: utf-8 -*-
from odoo import fields, models, api, _



class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_cash_in_out = fields.Boolean(
        string='Enable Cash In/Out',
        default=False,
    )
