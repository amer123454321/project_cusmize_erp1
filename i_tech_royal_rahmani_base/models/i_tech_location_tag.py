# -*- coding: utf-8 -*-

from datetime import datetime
import math
from markupsafe import Markup
from odoo import api, fields, models,_
from random import randint

from odoo.exceptions import ValidationError

class ITechLocationTag(models.Model):

    _name = 'i.tech.location.tag'
    _description = 'Location Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('location_product_uniq', 'unique(location_id, product_id)',
         'Tag already exists for this product and location!')
    ]

    
    tag_ids = fields.Many2many(
        'i.tech.location.tag.line',
        'i_tech_location_tag_rel',   # relation table
        'tag_id',                    # this model column
        'line_id',                   # other model column
        string='Tags',
        required=True
    )
    product_id = fields.Many2one('product.template','Product', required=True)
    location_id = fields.Many2one('stock.location','Location', required=True)




    @api.constrains('product_id', 'location_id')
    def _check_unique_product_location(self):
        for rec in self:
            if not rec.product_id or not rec.location_id:
                continue

            domain = [
                ('id', '!=', rec.id),
                ('product_id', '=', rec.product_id.id),
                ('location_id', '=', rec.location_id.id),
            ]

            if self.search_count(domain):
                raise ValidationError(
                    _('Tag already exists for this product and location!')
                )



class ITechLocationTagLine(models.Model):

    _name = 'i.tech.location.tag.line'
    _description = 'Location Tag Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_color(self):
        return randint(1, 11)


    
    name = fields.Char('Tag Name', required=True, translate=True)
    
    location_id = fields.Many2one('stock.location','Location')
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (location_id,product_id,tag_id)', "Tag already exists!"),
    ]
