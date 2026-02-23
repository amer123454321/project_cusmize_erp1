from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_level = fields.Selection([
        ('normal', 'Normal'),
        ('vip', 'VIP'),
        ('dealer', 'Dealer'),
    ], default='normal', tracking=True)

    max_discount = fields.Float(
        string='Max Discount (%)',
        default=0.0
    )

    credit_limit = fields.Monetary(
        string='Credit Limit',
        currency_field='company_currency_id',
        company_dependent=True
    )


    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    current_credit = fields.Monetary(
        string='Current Credit',
        related='credit',
        currency_field='company_currency_id',
        readonly=True
    )

    allowed_currency_ids = fields.Many2many(
        'res.currency',
        string='Allowed Currencies'
    )

    def _onchange_customer_level(self):
        discount_map = {
            'normal': 0.0,
            'vip': 10.0,
            'dealer': 20.0,
        }
        if self.customer_level:
             self.max_discount = discount_map.get(self.customer_level, 0.0)

    @api.constrains('max_discount')
    def _check_max_discount(self):
        for record in self:
            if not 0 <= record.max_discount <= 100:
                raise ValidationError('Max discount must be between 0 and 100%.')












