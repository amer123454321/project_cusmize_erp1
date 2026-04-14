from odoo import models, api


class IrFilterDemo(models.AbstractModel):
    _name = 'ir.filter.demo'

    @api.model
    def create_demo_filter(self):

        model = 'account.move'

        existing = self.env['ir.filters'].search([
            ('name', '=', 'My Draft Invoices'),
            ('model_id', '=', model)
        ], limit=1)

        if not existing:
            self.env['ir.filters'].create({
                'name': 'My Draft Invoices',
                'model_id': model,
                'domain': "[('state','=','draft')]",
                'is_default': True,
                'user_id': self.env.user.id,
            })


class IrFilterDemo(models.AbstractModel):
    _name = 'ir.filter.demo'

    @api.model
    def create_demo_filter(self):

        model = 'account.move'

        existing = self.env['ir.filters'].search([
            ('name', '=', 'My Draft Invoices'),
            ('model_id', '=', model)
        ], limit=1)

        if not existing:
            self.env['ir.filters'].create({
                'name': 'My Draft Invoices',
                'model_id': model,
                'domain': "[('state','=','draft')]",
                'is_default': True,
                'user_id': self.env.user.id,
            })





