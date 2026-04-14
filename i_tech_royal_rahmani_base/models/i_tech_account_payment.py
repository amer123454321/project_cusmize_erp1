# -*- coding: utf-8 -*-

from datetime import datetime
import math
from markupsafe import Markup
from odoo import api, fields, models,_
from random import randint

from odoo.exceptions import ValidationError

class ITechAccountPayment(models.TransientModel):
    _name = 'i.tech.account.payment'
    _description = 'Account Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Custom Payment')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    salesperson_user_id = fields.Many2one('res.users','Salesperson')


    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        tracking=True,
        required=True
    )
    


    account_move_ids = fields.Many2many(
        'account.move',
        string='Invoices / Bills'
    )
    move_type = fields.Selection(
        selection=[
            ('entry', 'Journal Entry'),
            ('out_invoice', 'Customer Invoice'),
            ('out_refund', 'Customer Credit Note'),
            ('in_invoice', 'Vendor Bill'),
            ('in_refund', 'Vendor Credit Note'),
            ('out_receipt', 'Sales Receipt'),
            ('in_receipt', 'Purchase Receipt'),
        ],
        string='Type',
        required=True,
        readonly=True,
        tracking=True,
    )

    

    line_ids = fields.One2many(
        'i.tech.account.payment.line',
        'payment_id',
        string='Lines'
    )

    # @api.depends('line_ids.amount')
    # def _compute_total_amount(self):
    #     for rec in self:
    #         rec.total_amount = sum(rec.line_ids.mapped('amount'))

    total_due_amount = fields.Monetary(
        string="Total Due Amount",
        currency_field='partner_currency_id',  # عملة العميل
        compute='_compute_total_due_amount',
        store=True,
    )

    partner_currency_id = fields.Many2one(
        'res.currency',
        string='Partner Currency',
        compute='_compute_partner_currency',
        store=True,
    )

    total_payment = fields.Monetary(
        string="Total payment",
        currency_field='partner_currency_id',  
        compute='_compute_total_payment_and_remaining_amount',
        store=True,
    )
    remaining_amount = fields.Monetary(
        string="Remaining Amount",
        currency_field='partner_currency_id',  
        compute='_compute_total_payment_and_remaining_amount',
        store=True,
    )


    @api.depends('partner_id')
    def _compute_partner_currency(self):
        for rec in self:
            rec.partner_currency_id = rec.partner_id.i_tech_property_currency_id or rec.company_id.currency_id

    @api.depends('account_move_ids.amount_residual', 'account_move_ids.currency_id', 'partner_id')
    def _compute_total_due_amount(self):
        for rec in self:
            total = 0.0
            partner_currency = rec.partner_id.i_tech_property_currency_id or rec.company_id.currency_id
            for invoice in rec.account_move_ids:
                residual_in_partner_currency = invoice.currency_id._convert(
                    invoice.amount_residual,
                    partner_currency,
                    invoice.company_id,
                    rec.payment_date or fields.Date.today(),
                )
                total += residual_in_partner_currency
            rec.total_due_amount = total



    @api.depends('total_payment','line_ids','line_ids.partner_amount','line_ids.partner_currency_id')
    def _compute_total_payment_and_remaining_amount(self):
        for rec in self:
            total_payment = 0.0
            partner_currency = rec.partner_currency_id or rec.company_id.currency_id
            for line in rec.line_ids:
                if line.partner_amount:
                    amount_in_partner_currency = line.partner_currency_id._convert(
                        line.partner_amount,
                        rec.partner_currency_id,
                        rec.company_id,
                        rec.payment_date or fields.Date.today()
                    )
                    total_payment += amount_in_partner_currency
            remaining_amount = rec.total_due_amount - total_payment

            rec.total_payment = total_payment
            rec.remaining_amount = remaining_amount


    def action_create_payments(self):
        Payment = self.env['account.payment']

        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("There are no lines to create payments."))

            for line in rec.line_ids:
                if not line.cash_amount or line.cash_amount <= 0:
                    continue
                payment_type = False
                partner_type = False
                if rec.move_type == 'out_invoice':
                   payment_type = 'inbound'
                   partner_type = 'customer'
                elif rec.move_type == 'in_invoice':  
                    payment_type = 'outbound'
                    partner_type = 'supplier'
                else:
                    raise ValidationError(_("Unsupported accounting move type."))
                payment_vals = {
                    'payment_type': payment_type, 
                    'partner_type': partner_type,
                    'partner_id': rec.partner_id.id,
                    'amount': abs(line.cash_amount),
                    'currency_id': line.cash_currency_id.id,
                    'journal_id': line.journal_id.id,
                    'date': rec.payment_date,
                    'memo': rec.name or 'Custom Payment',
                    'company_id': rec.company_id.id,
                    'salesperson_user_id' : rec.salesperson_user_id.id
                }

                if line.discount_amount < 0:
                    write_off_lines = []
                    company_currency = rec.company_id.currency_id

                    balance = line.cash_currency_id._convert(
                        line.discount_amount,
                        company_currency,
                        rec.company_id,
                        rec.payment_date,
                    )

                    write_off_lines.append({
                        'name': _('Cash'),
                        'account_id': line.journal_id.default_account_id.id,  # يفضّل حساب خصم
                        'currency_id': line.cash_currency_id.id,
                        'amount_currency': line.discount_amount,
                        'balance': balance,
                    })
                    write_off_lines.append({
                        'name': _('Discount'),
                        'account_id': line.account_id.id,  # يفضّل حساب خصم
                        'currency_id': line.cash_currency_id.id,
                        'amount_currency': -line.discount_amount,
                        'balance': -balance,
                    })
                    payment_vals['write_off_line_vals'] = write_off_lines

                payment = Payment.create(payment_vals)
                payment.action_post()
                invoice_line_ids = payment.move_id.invoice_line_ids
                for invoice_line in invoice_line_ids:
                    
                    if invoice_line.account_id.id in (rec.partner_id.property_account_receivable_id.id , rec.partner_id.property_account_payable_id.id):
                        partner_amount = payment.currency_id._convert(
                            payment.amount,
                            line.partner_currency_id,
                            rec.company_id,
                            rec.payment_date,
                        )
                        invoice_line.currency_id = line.partner_currency_id.id
                        invoice_line.amount_currency = -partner_amount if rec.partner_id.property_account_receivable_id.id else partner_amount
                        

                if rec.account_move_ids:
                    for invoice in rec.account_move_ids:
                        invoice_lines = invoice.line_ids.filtered(lambda l: l.account_id == rec.partner_id.property_account_receivable_id or l.account_id == rec.partner_id.property_account_payable_id)
                        payment_lines = payment.move_id.line_ids.filtered(lambda l: l.account_id == rec.partner_id.property_account_receivable_id or l.account_id == rec.partner_id.property_account_payable_id)
                        if invoice_lines and payment_lines:
                            (invoice_lines + payment_lines).reconcile()        

               




class ITechAccountPaymentLine(models.TransientModel):
    _name = 'i.tech.account.payment.line'
    _description = 'Account Payment Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    payment_id = fields.Many2one('i.tech.account.payment', string='Payment', ondelete='cascade', required=True)
    company_id = fields.Many2one('res.company', related='payment_id.company_id', store=True)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    account_id = fields.Many2one('account.account', string='Discount Account')
    cash_currency_id = fields.Many2one('res.currency', string='Cash Currency', store=True)
    partner_currency_id = fields.Many2one('res.currency', string='Partner Currency', store=True)
    company_currency_id = fields.Many2one('res.currency', string='Company Currency',related='company_id.currency_id', store=True, readonly=True)
    # original_rate = fields.Float(string='Rate', digits=(12, 6))
    rate = fields.Float(string='Rate')
    amount = fields.Monetary(string='Amount', currency_field='cash_currency_id')
    cash_amount = fields.Monetary(string='Cash Amount', currency_field='cash_currency_id',compute="_compute_amounts")
    discount_amount = fields.Monetary(string='Discount Amount', currency_field='cash_currency_id',compute="_compute_amounts")
    # original_amount = fields.Monetary(string='original Amount', currency_field='company_currency_id',compute="_compute_amounts")
    partner_amount = fields.Monetary(string='Partner Amount', currency_field='partner_currency_id',compute="_compute_amounts")




    @api.depends('cash_currency_id','rate','amount','partner_currency_id')
    def _compute_amounts(self):
        for rec in self:
            # original_amount = 0
            amount = rec.amount
            if amount and rec.rate:   
                i_tech_custom_pay_rounding = rec.partner_currency_id.i_tech_custom_pay_rounding
                if rec.cash_currency_id == rec.partner_currency_id:
                    if rec.cash_currency_id == rec.company_currency_id:
                        pivot_currency_id = self.env['res.currency'].search([('pivot_currency_id','=',True)],limit=1)
                        original_rate = rec.cash_currency_id._get_conversion_rate(pivot_currency_id,rec.cash_currency_id,rec.company_id,rec.payment_id.payment_date)
                        rec.partner_amount = math.ceil((amount / rec.rate * original_rate) / i_tech_custom_pay_rounding) * i_tech_custom_pay_rounding if i_tech_custom_pay_rounding else amount / rec.rate * original_rate
                        rec.cash_amount = rec.partner_amount
                        rec.discount_amount = amount - rec.cash_amount
                    else:
                        original_rate = rec.cash_currency_id._get_conversion_rate(rec.company_currency_id,rec.cash_currency_id,rec.company_id,rec.payment_id.payment_date)
                        rec.partner_amount = math.ceil((amount * rec.rate * original_rate) / i_tech_custom_pay_rounding) * i_tech_custom_pay_rounding if i_tech_custom_pay_rounding else amount * rec.rate * original_rate
                        rec.cash_amount = rec.partner_amount
                        rec.discount_amount = amount - rec.cash_amount
                else:
                    if rec.cash_currency_id == rec.company_currency_id:
                        rec.partner_amount = math.ceil((amount / rec.rate) / i_tech_custom_pay_rounding) * i_tech_custom_pay_rounding if i_tech_custom_pay_rounding else amount / rec.rate
                        original_rate = rec.cash_currency_id._get_conversion_rate(rec.partner_currency_id,rec.cash_currency_id,rec.company_id,rec.payment_id.payment_date)
                        rec.cash_amount = rec.partner_amount * original_rate
                        rec.discount_amount = amount - rec.cash_amount
                    else:
                        original_rate = rec.cash_currency_id._get_conversion_rate(rec.cash_currency_id,rec.partner_currency_id,rec.company_id,rec.payment_id.payment_date)
                        rec.partner_amount = math.ceil((amount * rec.rate ) / i_tech_custom_pay_rounding) * i_tech_custom_pay_rounding if i_tech_custom_pay_rounding else amount * rec.rate
                        rec.cash_amount = rec.partner_amount / original_rate
                        rec.discount_amount = amount - rec.cash_amount 

                if rec.discount_amount > 0:
                    rec.discount_amount = 0

            else:
                rec.partner_amount = 0
                rec.cash_amount = 0
                rec.discount_amount = 0

            




                 








