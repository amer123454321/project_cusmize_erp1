from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ====== Profit Fields ======
    total_cost = fields.Monetary(
        string="Total Cost",
        compute="_compute_profit_data",
        store=True,
        currency_field='currency_id'
    )

    profit_amount = fields.Monetary(
        string="Profit",
        compute="_compute_profit_data",
        store=True,
        currency_field='currency_id'
    )

    profit_margin = fields.Float(
        string="Profit Margin (%)",
        compute="_compute_profit_data",
        store=True
    )

    @api.depends(
        'order_line.product_uom_qty',
        'order_line.product_id.standard_price',
        'amount_untaxed'
    )
    def _compute_profit_data(self):
        for order in self:
            total_cost = 0.0
            for line in order.order_line:
                purchase_price = line.product_id.standard_price
                total_cost += purchase_price * line.product_uom_qty


            order.total_cost = total_cost
            order.profit_amount = order.amount_untaxed - total_cost
            order.profit_margin = (order.profit_amount / order.amount_untaxed * 100
                                   if order.amount_untaxed else 0.0)
    def _check_inventory_before_confirm(self):
        for order in self:
            for line in order.order_line:
                product = line.product_id

                if product.type != 'product':
                    continue

                required_qty = line.product_uom_qty
                qty_available = product.qty_available
                virtual_qty = product.virtual_available
                reserved_qty = qty_available - virtual_qty

                if required_qty > qty_available:
                    raise UserError(_(
                        "🚨 Insufficient Stock\n\n"
                        "Product: %(product)s\n"
                        "Requested: %(req)s\n"
                        "Available: %(avail)s\n"
                        "Reserved: %(reserved)s"
                    ) % {
                        'product': product.display_name,
                        'req': required_qty,
                        'avail': qty_available,
                        'reserved': reserved_qty,
                    })

    # ====== Confirm Action with Business Logic ======
    def action_confirm(self):
        for order in self:
            partner = order.partner_id
            company = order.company_id
            user = self.env.user

            # 👑 Business Admin يتجاوز كل شيء
            if user.has_group('project_cusmize_erp.group_business_admin'):
                return super().action_confirm()

            if partner.allowed_currency_ids and order.currency_id not in partner.allowed_currency_ids:
                raise UserError(
                    _("Currency %s is not allowed for this customer.") % order.currency_id.name
                )

            order_amount_company = order.currency_id._convert(
                order.amount_total,
                company.currency_id,
                company,
                order.date_order or fields.Date.context_today(self)
            )

            # 3️⃣ Credit Limit (Accounting Director يتجاوز فقط)
            if not user.has_group('project_cusmize_erp.group_accounting_director_custom'):
                if partner.credit_limit > 0:
                    total_credit = partner.current_credit + order_amount_company
                    if total_credit > partner.credit_limit:
                        raise UserError(_("⚠️ Credit Limit Exceeded"))

            # 4️⃣ Inventory Check (Sales & Manager يخضعوا)
            self._check_inventory_before_confirm()

            # 5️⃣ Discount Check
            max_allowed = company.max_discount_without_approval or 0.0

            # Sales Manager يقدر يتجاوز حد الشركة
            if not user.has_group('project_cusmize_erp.group_sales_team_manager_custom'):
                for line in order.order_line:
                    if line.discount > max_allowed:
                        raise UserError(_("⛔ Discount exceeds allowed limit"))

        return super().action_confirm()

    def _check_user_invoice_lock(self):
        user = self.env.user

        if not user.invoice_lock_enabled:
            return

        lock_days = user.invoice_lock_days or 0

        for record in self:
            if not record.date_order:
                continue

            order_date = fields.Datetime.from_string(record.date_order)
            limit_date = order_date + timedelta(days=lock_days)

            if datetime.now() > limit_date:
                raise UserError(
                    "لا يمكنك تعديل أو حذف هذا السجل لأنه تجاوز مدة القفل المحددة وهي %s يوم."
                    % lock_days
                )
    # ====== Optional: Locks for write/unlink ======
    def write(self, vals):
        self._check_user_invoice_lock()
        return super().write(vals)

    def unlink(self):
        self._check_user_invoice_lock()
        return super().unlink()
