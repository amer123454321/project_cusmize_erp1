# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.exceptions import ValidationError, UserError

class ITechAccountMoveLine(models.Model):
    _inherit = 'account.move.line'




    i_tech_hide_account = fields.Boolean('Hide Account',compute="_compute_i_tech_hide_account")

    transfer_discount = fields.Boolean('Transfer Discount')
    
    # @api.constrains('account_id', 'display_type')
    # def _check_payable_receivable(self):
    #     for line in self:
    #         transfer_discount = line.transfer_discount
    #         if line.move_id.is_sale_document(include_receipts=True):
    #             if transfer_discount:
    #                continue
            
    #         return super()._check_payable_receivable()
        
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        res = super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


        user = self.env.user
        if not user.has_group('i_tech_royal_rahmani_base.i_tech_hide_account_group'):
            hide_accounts = self.env['account.account'].sudo().search([('i_tech_hide_account','=',True)]).ids
            for group_line in res:
                account = group_line.get('account_id')
                if account and account[0] in hide_accounts:
                    group_line['debit'] = False 
                    group_line['credit'] = False 
                    group_line['amount_currency'] = False 
                    group_line['balance'] = False 
                    group_line['amount_residual'] = False 
                    group_line['amount_residual_currency'] = False 
            
        return res



    @api.depends('account_id')
    def _compute_i_tech_hide_account(self):
        for rec in self:
            i_tech_hide_account = False
            if rec.account_id.i_tech_hide_account:
                user = self.env.user
                if not user.has_group('i_tech_royal_rahmani_base.i_tech_hide_account_group'):
                    i_tech_hide_account = True

            rec.i_tech_hide_account = i_tech_hide_account




    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            if line.move_id.is_sale_document(include_receipts=True):
                transfer_discount = line.transfer_discount
                if transfer_discount:
                   continue
                if account_type == 'liability_payable':
                    raise UserError(_("Account %s is of payable type, but is used in a sale operation.", line.account_id.code))
                if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                    raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if account_type == 'asset_receivable':
                    raise UserError(_("Account %s is of receivable type, but is used in a purchase operation.", line.account_id.code))
                if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                    raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))

            