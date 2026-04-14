# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    accounting_lock = fields.Boolean('Accounting Lock')
    accounting_lock_date = fields.Integer('Accounting Lock Date')



    allowed_partner_types = fields.Many2many(comodel_name='i.tech.partner.type',
                                    string='Allowed Partners',
                                    help='Allowed Partners for users.')
