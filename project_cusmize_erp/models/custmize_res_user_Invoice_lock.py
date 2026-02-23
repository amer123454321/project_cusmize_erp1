from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    invoice_lock_enabled = fields.Boolean(
        string="Enable Invoice Lock"
    )

    invoice_lock_days = fields.Integer(
        string="Invoice Lock After (Days)",
        default=1
    )

    sale_order_ids = fields.One2many(
        'sale.order',
        'user_id',
        string="Sales Orders"
    )

    total_sales_amount = fields.Float(
        string="Total Sales Amount",
        compute="_compute_sales_stats",
        store=False
    )

    total_profit_amount = fields.Float(
        string="Total Profit Amount",
        compute="_compute_sales_stats",
        store=False
    )

    @api.depends('sale_order_ids.amount_untaxed', 'sale_order_ids.profit_amount', 'sale_order_ids.state')
    def _compute_sales_stats(self):
        for user in self:
            orders = user.sale_order_ids.filtered(
                lambda o: o.state in ['sale', 'done']
            )
            user.total_sales_amount = sum(orders.mapped('amount_untaxed'))
            user.total_profit_amount = sum(orders.mapped('profit_amount'))
