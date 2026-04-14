# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ITechAccountPayment(models.Model):
    _inherit = 'account.payment'

    salesperson_user_id = fields.Many2one('res.users','Salesperson')
    