# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pos_print_session_report = fields.Boolean(string='POS Print Session Report', groups='hr.group_hr_user')

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super(HrEmployee, self)._load_pos_data_fields(config_id) + ['pos_print_session_report']

