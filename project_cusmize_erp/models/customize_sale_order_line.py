from odoo import models, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('discount')
    def _onchange_discount_limit(self):
        user = self.env.user
        partner = self.order_id.partner_id

        # Sales Manager يتبع حد العميل فقط
        if user.has_group('project_cusmize_erp.group_sales_team_manager_custom'):
            max_allowed = partner.max_discount
        else:
            max_allowed = min(partner.max_discount, 10.0)  # مثال حد افتراضي

        if self.discount > max_allowed:
            raise UserError(_("Max allowed discount is %s%%") % max_allowed)
