# -*- coding: utf-8 -*-

from datetime import datetime
import math
from markupsafe import Markup
from odoo import fields, models,_
from random import randint

class i_tech_product_color_tag(models.Model):

    _name = 'i.tech.product.color.tag'
    _description = 'Product Color Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Color Name', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


