# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import ast
import datetime
import json
from collections import Counter

from odoo import fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_session_report = fields.Boolean(string="Enable Session  Report")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_session_report = fields.Boolean(related='pos_config_id.enable_session_report', readonly=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    payment_method_line_ids = fields.One2many(
        'pos.payment.method.line', 'session_id', string='Payment Method Lines',
        help='List of payment methods used in this session.',
        compute='_compute_payment_method_lines'

    )

    def _compute_payment_method_lines(self):
        PaymentMethodLine = self.env['pos.payment.method.line']
        for session in self:
            session.payment_method_line_ids.unlink()

            payments = self.env['pos.payment'].search([
                ('session_id', '=', session.id),
                ('pos_order_id.state', 'in', ['done', 'paid', 'invoiced']),
                ('amount', '!=', 0)
            ])

            method_data = {}
            for payment in payments:
                method_id = payment.payment_method_id.id
                if method_id not in method_data:
                    method_data[method_id] = {'amount': 0.0, 'count': 0}
                method_data[method_id]['amount'] += payment.amount
                method_data[method_id]['count'] += 1

            for method_id, values in method_data.items():
                PaymentMethodLine.create({
                    'session_id': session.id,
                    'payment_method_id': method_id,
                    'amount': values['amount'],
                    'count': values['count'],
                })

    # def _get_pos_ui_hr_employee(self, params):
    #     employee_data = super(PosSession, self)._get_pos_ui_hr_employee(params)
    #     for emp in employee_data:
    #         employee = self.env['hr.employee'].sudo().browse(emp['id'])
    #         emp['print_session_report_allowed'] = employee.pos_print_session_report
    #     return employee_data

    def view_session_report(self):
        return self.env.ref('bi_pos_closed_session_reports.action_report_session_z').report_action(self)

    def get_current_datetime(self):
        current = fields.datetime.now()
        return current.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_opened_date(self):
        return datetime.datetime.strptime(str(self.start_at), DEFAULT_SERVER_DATETIME_FORMAT)

    def get_closed_date(self):
        if self.stop_at:
            return datetime.datetime.strptime(str(self.stop_at), DEFAULT_SERVER_DATETIME_FORMAT)

    def get_session_amount_data(self):
        pos_order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        discount_amount = 0.0
        taxes_amount = 0.0
        total_sale_amount = 0.0
        total_gross_amount = 0.0
        total_refund_amount = 0.0
        sold_product = {}
        for pos_order in pos_order_ids:
            currency = pos_order.session_id.currency_id
            # total_gross_amount += pos_order.lines.price_unit * pos_order.lines.qty

            for line in pos_order.lines:
                total_gross_amount += line.price_unit * line.qty

                if line.qty < 0:
                    total_refund_amount += line.price_unit * line.qty

                # if line.product_id.pos_categ_id and line.product_id.pos_categ_id.name:
                #     if line.product_id.pos_categ_id.name in sold_product:
                #         sold_product[line.product_id.pos_categ_id.name] += line.qty
                #     else:
                #         sold_product.update({line.product_id.pos_categ_id.name: line.qty})
                if line.product_id.pos_categ_ids and line.product_id.pos_categ_ids[:1].name:
                    category_name = line.product_id.pos_categ_ids[:1].name
                    if category_name in sold_product:
                        sold_product[category_name] += line.qty
                    else:
                        sold_product.update({category_name: line.qty})
                else:
                    if 'undefine' in sold_product:
                        sold_product['undefine'] += line.qty
                    else:
                        sold_product.update({'undefine': line.qty})
                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty,
                        product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes_amount += tax.get('amount', 0)
                if line.discount > 0:
                    discount_amount += (((line.price_unit * line.qty) * line.discount) / 100)
                if line.qty > 0:
                    total_sale_amount += line.price_unit * line.qty
        # print('total_gross_amount3', total_gross_amount)
        return {
            'total_sale': total_gross_amount,
            'discount': discount_amount,
            'tax': taxes_amount,
            'products_sold': sold_product,
            'total_gross': total_gross_amount - taxes_amount - discount_amount,
            'final_total': (total_gross_amount - discount_amount),
            'total_refund': total_refund_amount
        }

    def get_taxes_data(self):
        order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        taxes = {}
        for order in order_ids:
            currency = order.pricelist_id.currency_id
            for line in order.lines:
                if line.tax_ids_after_fiscal_position:
                    for tax in line.tax_ids_after_fiscal_position:
                        discount_amount = 0
                        if line.discount > 0:
                            discount_amount = ((line.qty * line.price_unit) * line.discount) / 100
                        untaxed_amount = (line.qty * line.price_unit) - discount_amount
                        tax_percentage = 0
                        if tax.amount_type == 'group':
                            for child_tax in tax.children_tax_ids:
                                tax_percentage += child_tax.amount
                        else:
                            tax_percentage += tax.amount

                        tax_amount = ((untaxed_amount * tax_percentage) / 100)
                        if tax.name:
                            if tax.name in taxes:
                                taxes[tax.name] += tax_amount
                            else:
                                taxes.update({tax.name: tax_amount})
                        else:
                            if 'undefine' in taxes:
                                taxes['undefine'] += tax_amount
                            else:
                                taxes.update({'undefine': tax_amount})
        return taxes

    def get_pricelist(self):
        pos_order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        pricelist = {}
        for pos_order in pos_order_ids:
            if pos_order.pricelist_id.name:
                if pos_order.pricelist_id.name in pricelist:
                    pricelist[pos_order.pricelist_id.name] += pos_order.amount_total
                else:
                    pricelist.update({pos_order.pricelist_id.name: pos_order.amount_total})
            else:
                if 'undefine' in pricelist:
                    pricelist['undefine'] += pos_order.amount_total
                else:
                    pricelist.update({'undefine': pos_order.amount_total})
        return pricelist

    def get_pricelist_qty(self, pricelist):
        if pricelist:
            qty_pricelist = 0
            pricelist_obj = self.env['product.pricelist'].search([('name', '=', str(pricelist))])
            if pricelist_obj:
                pos_order_ids = self.env['pos.order'].search(
                    [('session_id', '=', self.id), ('pricelist_id.id', '=', pricelist_obj.id)])
                qty_pricelist = len(pos_order_ids)
            else:
                if pricelist == 'undefine':
                    pos_order_ids = self.env['pos.order'].search(
                        [('session_id', '=', self.id), ('pricelist_id', '=', False)])
                    qty_pricelist = len(pos_order_ids)
            return int(qty_pricelist)

    def get_payment_data(self):
        pos_order_ids = self.env['pos.order'].search([('session_id', '=', self.id)])
        st_line_ids = self.env["pos.payment"].search([('pos_order_id', 'in', pos_order_ids.ids)]).ids

        if st_line_ids:
            self.env.cr.execute("""
                                SELECT COALESCE(ppm.name ->>%s, ppm.name->>'en_US')             AS p_name,
                                       SUM(CASE WHEN pp.amount != 0 THEN pp.amount ELSE 0 END)  AS total,
                                       COUNT(CASE WHEN pp.amount != 0 THEN pp.id ELSE NULL END) AS p_count
                                FROM pos_payment AS pp
                                         INNER JOIN pos_payment_method AS ppm
                                                    ON pp.payment_method_id = ppm.id
                                WHERE pp.id IN %s
                                GROUP BY ppm.name
                                """, (self.env.lang, tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
            # print() st_line_ids with payment method



        else:
            payments = []

        return payments


def get_payment_qty(self, payment_method):
    qty_payment_method = 0
    if payment_method:
        orders = self.env['pos.order'].search([('session_id', '=', self.id)])
        st_line_obj = self.env["account.bank.statement.line"].search([('statement_id', 'in', orders.ids)])
        if len(st_line_obj) > 0:
            res = []
            for line in st_line_obj:
                res.append(line.journal_id.name)
            res_dict = ast.literal_eval(json.dumps(dict(Counter(res))))
            if payment_method in res_dict:
                qty_payment_method = res_dict[payment_method]
    return int(qty_payment_method)


class PaymentMethodLine(models.Model):
    _name = 'pos.payment.method.line'
    _description = 'POS Payment Method Line'

    session_id = fields.Many2one('pos.session', string='Session', required=True, ondelete='cascade')
    payment_method_id = fields.Many2one('pos.payment.method', string='Payment Method', required=True)
    amount = fields.Float(string='Amount', required=True, help='Amount of the payment method used in this session.')
    count = fields.Integer(string='Count', required=True,
                           help='Number of times this payment method was used in this session.')
