# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError



class ITechResCompany(models.Model):
    _inherit = "res.company"

    i_tech_use_sale_location_id = fields.Boolean('Use Sale Location')


    i_tech_sale_order_transfer_discount_account = fields.Many2one('account.account',string="Transfer Discount Account",)