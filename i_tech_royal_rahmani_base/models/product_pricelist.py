# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    i_tech_free_product_account_id = fields.Many2one('account.account',"Free Product Account",tracking=True)














