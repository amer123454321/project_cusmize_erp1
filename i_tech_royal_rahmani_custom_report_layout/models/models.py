from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = 'account.move'