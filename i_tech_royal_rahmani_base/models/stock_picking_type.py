# -*- coding: utf-8 -*-

import base64
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import _, float_is_zero


class ITechStockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    i_tech_use_color_tag = fields.Boolean(
        string='Use Color Tag',
        help='Enable color tagging on the product.'
    )





    