# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    def try_cash_in_out(self, _type, amount, reason, extras):
        return super(PosSession, self.sudo()).try_cash_in_out(_type, amount, reason, extras)

