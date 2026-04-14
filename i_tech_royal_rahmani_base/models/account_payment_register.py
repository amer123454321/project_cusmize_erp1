# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ITechAccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"



    i_tech_orgin_amount = fields.Float('Orgin Amount')
    i_tech_exchange_rate = fields.Float('Exchange Rate')
    i_tech_exchange_difference = fields.Float('Exchange Difference')
    i_tech_custom_user_rate = fields.Float()



    def _convert_to_wizard_currency(self, installments):
        res = super()._convert_to_wizard_currency(installments)

        if self.i_tech_exchange_rate:
            company_currency_id = self.env.company.currency_id
            if self.currency_id.id != company_currency_id.id:
                amount = self.currency_id._convert(
                            res,
                            company_currency_id,
                            self.env.company,
                            self.payment_date or fields.Date.today()
                        )
                return amount * self.i_tech_exchange_rate
        return res


    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        if self.i_tech_exchange_rate:
            if self.payment_difference_handling != 'open':
                raise UserError(_('You can not user (Mark as fully paid) with this exchange rate'))
            company_currency_id = self.env.company.currency_id
            if self.currency_id.id != company_currency_id.id:
                orgin_rate =  company_currency_id._get_conversion_rate(company_currency_id,self.currency_id,self.company_id,self.payment_date)
                if self.i_tech_exchange_rate != orgin_rate:
                    total_amount_values = self._get_total_amounts_to_pay(self.batches)
                    amount_by_default = total_amount_values['amount_by_default']
                    exchange_difference = amount_by_default - self.payment_difference - (self.amount / self.i_tech_exchange_rate  * orgin_rate)
                    exchange_difference_currency = self.currency_id._convert(
                        exchange_difference,
                        company_currency_id,
                        self.env.company,
                        self.payment_date or fields.Date.today()
                    )
                    res['write_off_line_vals'] = [{'name': 'Write-Off',
                                                   'account_id': self.journal_id.profit_account_id.id if exchange_difference > 0 else self.journal_id.loss_account_id.id,
                                                   'partner_id': self.partner_id.id, 'currency_id': self.currency_id.id,
                                                   'amount_currency': -exchange_difference,
                                                   'balance': -exchange_difference_currency}]
        return res









    @api.onchange('i_tech_exchange_rate','amount')
    def onchange_exchange_rate(self):
        for rec in self: 
                company_currency_id = self.env.company.currency_id
                if rec.currency_id.id != company_currency_id.id and self.i_tech_exchange_rate:
                    orgin_rate =  self.currency_id._get_conversion_rate(self.currency_id,company_currency_id,rec.company_id,rec.payment_date)
                    if self.i_tech_custom_user_rate == orgin_rate:
                        rec.i_tech_orgin_amount = rec.amount
                    else:
                        rec.i_tech_orgin_amount = self.currency_id._convert(
                            rec.amount,
                            company_currency_id,
                            self.env.company,
                            self.payment_date or fields.Date.today()
                        )






                    rec.i_tech_custom_user_rate = rec.i_tech_exchange_rate or orgin_rate
                    rec._compute_payment_difference()
                    rec._compute_show_payment_difference()


                    if self.i_tech_exchange_rate != orgin_rate: 
                        total_amount_values = self._get_total_amounts_to_pay(self.batches)
                        amount_by_default = total_amount_values['amount_by_default'] 
                        exchange_difference = amount_by_default - self.payment_difference - (self.amount / self.i_tech_exchange_rate  * orgin_rate)
                        exchange_difference_currency = self.currency_id._convert(
                            exchange_difference,
                            company_currency_id,
                            self.env.company,
                            self.payment_date or fields.Date.today()
                        )
                    else:
                        exchange_difference = 0

                    rec.i_tech_exchange_difference = exchange_difference


                else:
                    rec.i_tech_orgin_amount = 0
                    rec.i_tech_exchange_difference = 0
                    rec.i_tech_custom_user_rate = 0
                    rec._compute_payment_difference()
                    rec._compute_show_payment_difference()

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        company_currency_id = self.env.company.currency_id
        if not self.i_tech_exchange_rate and company_currency_id.id != self.currency_id.id:

            orgin_rate =  company_currency_id._get_conversion_rate(company_currency_id,self.currency_id,self.company_id,self.payment_date)
            self.i_tech_custom_user_rate = orgin_rate
            self.i_tech_exchange_rate = orgin_rate

        if not self.can_edit_wizard or not self.currency_id or not self.payment_date or not self.custom_user_amount:
            return

        total_amount_values = self._get_total_amounts_to_pay(self.batches)
        self.amount = total_amount_values['amount_by_default']




        
