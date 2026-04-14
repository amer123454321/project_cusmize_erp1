# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechProductTemplate(models.Model):
    _inherit = 'product.template'

    
    # standard_price = fields.Float(
    #     'Cost', compute='_compute_standard_price',
    #     inverse='_set_standard_price', search='_search_standard_price',
    #     digits='Product Price', groups="i_tech_royal_rahmani_base.i_tech_groups_view_cost_price",
    #     help="""Value of the product (automatically computed in AVCO).
    #     Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
    #     Used to compute margins on sale orders.""")





    i_tech_use_color_tag = fields.Boolean(
        string='Use Color Tag',
        help='Enable color tagging on the product.',
        tracking=True
    )







    i_tech_location_tag_ids = fields.One2many(
        'i.tech.location.tag',
        'product_id',
        string='Location Tags',
        tracking=True
    )