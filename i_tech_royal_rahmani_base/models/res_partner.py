# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.tools.image import UserError

class ITechResPartner(models.Model):
    _inherit = 'res.partner'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    
    is_driver = fields.Boolean('Is Driver',
        tracking=True)
    i_tech_require_driver_and_vehicle = fields.Boolean(
        string="Require Driver and Vehicle",
        tracking=True
    )


    i_tech_property_currency_id = fields.Many2one('res.currency','Currency')


    i_tech_partner_type_id = fields.Many2one('i.tech.partner.type','Partner Type')




    @api.onchange('i_tech_partner_type_id')
    def onchange_i_tech_partner_type_id(self):
        for rec in self:
            user = self.env.user
            if not user.has_group('i_tech_royal_rahmani_base.i_tech_partner_type_group'):
                raise UserError(_("You do not have permission to modify Partner Type "))
            
            if rec.i_tech_partner_type_id:
               rec.property_account_receivable_id = rec.i_tech_partner_type_id.property_account_receivable_id.id
               rec.property_account_payable_id = rec.i_tech_partner_type_id.property_account_payable_id.id
            else:
               rec.property_account_receivable_id = False
               rec.property_account_payable_id = False    




    @api.model_create_multi
    def create(self, values_list):
        partner_type = self.env.context.get('i_tech_partner_type_id')
        partner_type_id = self.env['i.tech.partner.type'].sudo().search([('type','=',partner_type)],limit=1)
        for vals in values_list:
            if partner_type_id and not vals.get('i_tech_partner_type_id'):
                vals['i_tech_partner_type_id'] = partner_type_id.id

        return super().create(values_list) 