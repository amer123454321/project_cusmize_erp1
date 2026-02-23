from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    invoice_lock_days = fields.Integer(
        string="Invoice Lock After (Days)",
        default=1
    )

    max_discount_without_approval = fields.Float(
        string="Max Discount Without Approval (%)",
        default=10.0
    )



