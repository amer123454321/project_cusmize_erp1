# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechResCurrency(models.Model):
    _inherit = 'res.currency'

    pivot_currency_id = fields.Boolean('Pivot Currency')
    i_tech_custom_pay_rounding = fields.Float('Custom Pay Rounding')


