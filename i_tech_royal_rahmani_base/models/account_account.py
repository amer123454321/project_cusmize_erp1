# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechAccountAccount(models.Model):
    _inherit = 'account.account'

    i_tech_use_custom_payment = fields.Boolean('Use in Custom Payment')


    i_tech_hide_account = fields.Boolean('Hide Account')



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_show_prices(self):
        self.ensure_one()

        product = self.env['product.product'].search([], limit=1)

        pricelist_1 = self.pricelist_id

        other_pricelist = self.env['product.pricelist'].search(
            [('id', '!=', pricelist_1.id)],
            limit=1
        )

        price_1 = pricelist_1._get_product_price(
            product,
            quantity=1.0,
            partner=self.partner_id,
        )

        price_2 = other_pricelist._get_product_price(
            product,
            quantity=1.0,
            partner=self.partner_id,
        ) if other_pricelist else 0.0

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Prices',
                'message': f"""
    Product: {product.name}
    Order Pricelist: {price_1}
    Other Pricelist: {price_2}
    """,
                'sticky': False,
            }
        }


