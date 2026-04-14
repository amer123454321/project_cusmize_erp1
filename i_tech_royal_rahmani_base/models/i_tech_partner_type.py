# -*- coding: utf-8 -*-

from datetime import datetime
import math
from markupsafe import Markup
from odoo import api, fields, models,_
from random import randint

from odoo.exceptions import ValidationError

class ITechPartnerType(models.Model):
    _name = 'i.tech.partner.type'
    _description = 'Partner Type'
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Partner Type must be unique!'),
    ]
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(
        string='Name',
        compute='_compute_name_type',
        store=True,
        tracking=True
    )

    type = fields.Selection([
        ('cash_customer','Cash Customer'),
        ('credit','Credit Customer'),
        ('local_vendor','Local Vendor'),
        ('foreign_vendor','Foreign Vendor'),
        ('driver','Driver'),
    ],string="Type",default="cash_customer",required=True,tracking=True)


    property_account_receivable_id = fields.Many2one('account.account',
        string="Account Receivable",
        domain="[('account_type', '=', 'asset_receivable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        ondelete='restrict',required=True)

    property_account_payable_id = fields.Many2one('account.account',
        string="Account Payable",
        domain="[('account_type', '=', 'liability_payable'), ('deprecated', '=', False)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        ondelete='restrict',required=True)
    


    @api.depends('type')
    def _compute_name_type(self):
        mapping = dict(self._fields['type'].selection)
        for rec in self:
            rec.name = mapping.get(rec.type)

    