# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechProductProduct(models.Model):
    _inherit = 'product.product'

    
    # standard_price = fields.Float(
    #     'Cost', company_dependent=True,
    #     digits='Product Price',
    #     groups="i_tech_royal_rahmani_base.i_tech_groups_view_cost_price",
    #     help="""Value of the product (automatically computed in AVCO).
    #     Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
    #     Used to compute margins on sale orders.""")


