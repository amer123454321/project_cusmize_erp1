# -*- coding: utf-8 -*-


from odoo import api, fields, models




class ITechStockWarehouse(models.Model):

    _inherit = 'stock.warehouse'
     
    i_tech_analytic_account = fields.Many2one('account.analytic.account','Analytic Account', tracking=True)
