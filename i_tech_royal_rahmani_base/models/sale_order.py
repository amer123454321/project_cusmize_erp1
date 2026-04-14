# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ITechSaleOrder(models.Model):
    _inherit = 'sale.order'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    


    i_tech_sale_type = fields.Selection([
        ('cash','Cash'),
        ('credit','Credit'),
    ],string="Sale Type",default="cash",store=True,compute='_compute_sale_order_type',required=True,tracking=True)







    i_tech_require_driver_and_vehicle = fields.Boolean(
        string="Require Driver and Vehicle",
        compute="_compute_i_tech_require_driver_and_vehicle",
        store=True,
        readonly=False,
        tracking=True
    )

    amount_before_discount = fields.Monetary(string="Amount Before Discount", store=True, compute='_compute_amounts', tracking=4)
    discount_amount = fields.Monetary(string="Discount Amount", store=True, compute='_compute_amounts', tracking=4)

    i_tech_analytic_account = fields.Many2one('account.analytic.account','Analytic Account', compute='_compute_i_tech_analytic_account', store=True,readonly=False, tracking=4)

    i_tech_sale_order_transfer_discount = fields.Monetary(
        string="Transfer Discount",
        currency_id='currency_id'
    )
    i_tech_used_transfer_discount_in_invoice = fields.Boolean(
        string="Used Transfer Discount in Invoice",
        default=False,
        tracking=True
    )




    @api.depends('partner_id')
    def _compute_sale_order_type(self):
        for rec in self:
            i_tech_sale_type = 'cash'
            if rec.partner_id:
                if rec.partner_id.i_tech_partner_type_id.type == 'credit':
                    i_tech_sale_type = 'credit'           
            rec.i_tech_sale_type = i_tech_sale_type

    @api.onchange('warehouse_id')
    def onchange_i_tech_warehouse_id(self):
        for rec in self:
            for line in rec.order_line:
             line.i_tech_location_id = False



    @api.depends('warehouse_id')
    def _compute_i_tech_analytic_account(self):
        for rec in self:
            if rec.warehouse_id:
               rec.i_tech_analytic_account = rec.warehouse_id.i_tech_analytic_account.id


    @api.onchange('i_tech_analytic_account')
    def onchange_i_tech_analytic_account(self):
        for rec in self:
            for line in rec.order_line:
             line.analytic_distribution = {rec.i_tech_analytic_account.id: 100.00}
    
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id')
    def _compute_amounts(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            

            amount_before_discount = sum(
                line.price_unit * line.product_uom_qty
                for line in order_lines
            )
            order.amount_before_discount = amount_before_discount
            order.discount_amount = amount_before_discount - order.amount_untaxed 


            order.amount_untaxed = tax_totals['base_amount_currency']
            order.amount_tax = tax_totals['tax_amount_currency']
            order.amount_total = tax_totals['total_amount_currency']






    @api.depends('partner_id')
    def _compute_i_tech_require_driver_and_vehicle(self):
        for rec in self:
            rec.i_tech_require_driver_and_vehicle = rec.partner_id.i_tech_require_driver_and_vehicle

    def _get_warehouse_sequence(self, warehouse,company_id):
        """
        Get or create a sequence for a specific warehouse
        """
        seq_code = f"sale.order.{warehouse.code.lower()}"

        sequence = self.env['ir.sequence'].search([
            ('code', '=', seq_code),
            ('company_id', '=', company_id)
        ], limit=1)

        if not sequence:
            sequence = self.env['ir.sequence'].create({
                'name': f'Sales Order {warehouse.code}',
                'code': seq_code,
                'prefix': f'S-{warehouse.code}-',
                'padding': 5,
                'company_id': company_id,
                'implementation': 'standard',
            })

        return sequence

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and vals.get('warehouse_id'):
            company_id = vals['company_id'] if vals['company_id'] else self.env.company.id
            warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
            sequence = self._get_warehouse_sequence(warehouse,company_id)
            vals['name'] = sequence.next_by_id()

        return super().create(vals)
    

    def write(self, vals):
        if 'warehouse_id' in vals:
            for order in self:                 
                if order.state == 'draft':
                    company_id = vals['company_id'] if 'company_id' in vals else self.company_id.id
                    warehouse = self.env['stock.warehouse'].browse(vals['warehouse_id'])
                    sequence = order._get_warehouse_sequence(warehouse,company_id)
                    vals['name'] = sequence.next_by_id()
                else:
                    raise UserError(
                        _("You cannot change the warehouse after the Sales Order number is generated.")
                    )

        return super().write(vals)