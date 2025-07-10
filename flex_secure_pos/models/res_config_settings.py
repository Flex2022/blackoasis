# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_cash_in_out = fields.Boolean(
        related='pos_config_id.use_cash_in_out',
        readonly=False,
    )
