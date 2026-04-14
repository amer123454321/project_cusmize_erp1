# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.tools.image import UserError
from datetime import timedelta

class ITechAccountMove(models.Model):
    _inherit = 'account.move'

    i_tech_sale_order_transfer_discount = fields.Monetary(
        string="Transfer Discount",
        currency_id='currency_id'
    )

    without_access = fields.Boolean('Without Access')


    # line_ids = fields.One2many(
    #     'account.move.line',
    #     'move_id',
    #     string='Journal Items',
    #     copy=True,
    #     domain=lambda self: self._get_invoice_line_domain(),
    # )

    # @api.model
    # def _get_invoice_line_domain(self):
    #     user = self.env.user
    #     if not user.has_group('i_tech_royal_rahmani_base.i_tech_hide_account_group'):
    #         hide_accounts = self.env['account.account'].sudo().search([('i_tech_hide_account','=',True)]).ids
    #         return [('account_id', 'not in', hide_accounts)]
    #     else:
    #         return []



    def write(self, vals):
        for record in self:

            if self.env.user.accounting_lock and not record.without_access and record.create_date.date():
                if 'invoice_line_ids' in vals or 'state' in vals:
                    created_date = record.create_date.date()
                    today = fields.datetime.today().date()
                    accounting_lock_date = record.env.user.accounting_lock_date
                    days_ago = today - timedelta(days=accounting_lock_date)
                    if days_ago > created_date:
                        raise UserError("You do not have permission to modify this document " + record.name)
        res = super(ITechAccountMove, self).write(vals)


        return res

    def unlink(self):

        for record in self:
            if self.env.user.accounting_lock and not record.without_access and record.create_date.date():
                created_date = record.create_date.date()
                today = fields.datetime.today().date()
                accounting_lock_date = record.env.user.accounting_lock_date
                days_ago = today - timedelta(days=accounting_lock_date)
                if days_ago > created_date:
                    raise UserError("You do not have permission to delete this document " + record.name)



        res = super(ITechAccountMove,self).unlink()


        return res
    

    
            

    def button_draft(self):
        for move in self:
            sale_order = move.invoice_line_ids.sale_line_ids.mapped('order_id')[:1]
            sale_order.i_tech_used_transfer_discount_in_invoice = False
            move.i_tech_sale_order_transfer_discount = 0
        return super().button_draft()




    def _stock_account_prepare_anglo_saxon_out_lines_vals(self):
        lines_vals_list = super()._stock_account_prepare_anglo_saxon_out_lines_vals()

        # إعادة بناء القائمة لتضمين analytic_distribution لكل سطر مرتبط
        new_lines_vals_list = []
        for move in self:
            anglo_saxon_price_ctx = move._get_anglo_saxon_price_ctx() if move.is_sale_document(include_receipts=True) else {}
            for line in move.invoice_line_ids:
                # التأكد أن الخط مؤهل للـ COGS
                if not line._eligible_for_cogs():
                        continue

                # البحث عن السطور الأصلية في lines_vals_list المطابقة لهذا الخط
                for l in lines_vals_list:
                    if l.get('cogs_origin_id') == line.id:
                        # إضافة الحقل analytic_distribution
                        l['analytic_distribution'] = line.analytic_distribution
                        sale_order_line = self.env['sale.order.line'].sudo().search([('invoice_lines','in',line.ids)],limit=1)
                        if l['account_id'] and l['price_unit'] < 0 and sale_order_line.i_tech_free_product and sale_order_line.order_id.pricelist_id.i_tech_free_product_account_id:
                            l['account_id'] = sale_order_line.order_id.pricelist_id.i_tech_free_product_account_id.id
                        new_lines_vals_list.append(l)



            # مصاريف النقل
            sale_order = move.invoice_line_ids.sale_line_ids.mapped('order_id')[:1]
            if sale_order:
                if sale_order.i_tech_sale_order_transfer_discount and not sale_order.i_tech_used_transfer_discount_in_invoice:

                    price_unit = sale_order.i_tech_sale_order_transfer_discount
                    analytic_distribution = {sale_order.i_tech_analytic_account.id: 100.00}
                    new_line_vals = {
                        'name': f'Discount',
                        'move_id': move.id,
                        'partner_id': move.commercial_partner_id.id,
                        'quantity': 1,
                        # 'debit': amount_currency,
                        'currency_id' : move.currency_id.id,
                        'amount_currency': price_unit,
                        'account_id': move.company_id.i_tech_sale_order_transfer_discount_account.id,
                        'analytic_distribution' : analytic_distribution ,
                        'display_type': 'cogs',
                        'transfer_discount' : True,
                        'tax_ids': [],
                    }

                    new_lines_vals_list.append(new_line_vals)


                    new_line_vals = {
                        'name': f'Discount',
                        'move_id': move.id,
                        'partner_id': move.commercial_partner_id.id,
                        'quantity': 1,
                        # 'credit': amount_currency,
                        'currency_id' : move.currency_id.id,
                        'amount_currency': -price_unit,
                        'account_id': move.partner_id.property_account_receivable_id.id,
                        'analytic_distribution' : analytic_distribution,
                        'display_type': 'cogs',
                        'transfer_discount' : True,
                        'tax_ids': [],
                    }

                    new_lines_vals_list.append(new_line_vals)








                    sale_order.i_tech_used_transfer_discount_in_invoice = True
                    move.i_tech_sale_order_transfer_discount = price_unit









        return new_lines_vals_list













    def action_open_i_tech_account_payment_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id("i_tech_royal_rahmani_base.action_i_tech_account_payment")
        partner_id = self.mapped('partner_id')[0].id  # أول عميل (لأن الجميع نفس العميل)
        move_type = self.mapped('move_type')[0]  
        action['context'] = {
            'default_partner_id': partner_id,
            'default_move_type': move_type,
            'default_account_move_ids':self.ids,
            }
        return action
    

    def action_force_open_i_tech_account_payment_wizard(self):
        if any(m.payment_state not in ('not_paid', 'partial', 'in_payment') for m in self):
            raise UserError(_("You can only register payments for (partially) unpaid documents."))
        if any(m.move_type == 'entry' for m in self):
            raise UserError(_("You cannot register payments for miscellaneous entries."))
        partner_ids = self.mapped('partner_id')
        if len(partner_ids) > 1:
            raise UserError(_("You can only register payments for one customer at a time."))
        move_types = set(self.mapped('move_type'))
        if len(move_types) > 1:
            raise UserError(_("All selected documents must have the same type."))
        return self.action_open_i_tech_account_payment_wizard()

























class ITechAccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_tax_totals_summary(
        self, base_lines, currency, company, cash_rounding=None
    ):
        tax_totals_summary = super()._get_tax_totals_summary(
            base_lines, currency, company, cash_rounding=cash_rounding
        )

        amount_before_discount_currency = 0.0
        discount_amount_currency = 0.0

        for line in base_lines:
            qty = line.get('quantity', 1.0)
            price_unit = line.get('price_unit', 0.0)


            if price_unit >= 0:
                amount_before_discount_currency += qty * price_unit
           

        
            


        base_amount_currency = tax_totals_summary.get(
            'base_amount_currency', 0.0
        )
        discount_amount_currency = (
            amount_before_discount_currency - base_amount_currency
        )

        if base_lines:
            if base_lines[0]['record']. _name == 'sale.order.line':
               discount_amount_currency += base_lines[0]['record'].order_id.i_tech_sale_order_transfer_discount
            elif base_lines[0]['record']. _name == 'account.move.line':
               discount_amount_currency += base_lines[0]['record'].move_id.i_tech_sale_order_transfer_discount
               
        tax_totals_summary.update({
            'amount_before_discount_currency': amount_before_discount_currency,
            'discount_amount_currency': discount_amount_currency,
        })

        return tax_totals_summary




