# -*- coding: utf-8 -*-

import base64
from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import _, float_is_zero


class ITechStockPicking(models.Model):

    _inherit = 'stock.picking'
     
    i_tech_driver_id = fields.Many2one('res.partner','Driver',tracking=True)
    i_tech_vehicle_number = fields.Char('Vehicle Number',tracking=True)
    i_tech_require_driver_and_vehicle = fields.Boolean(
        string="Require Driver and Vehicle",
        compute="_compute_i_tech_require_driver_and_vehicle",
        store=True,
        tracking=True
    )

    @api.depends('sale_id','sale_id.partner_id','sale_id.i_tech_require_driver_and_vehicle')
    def _compute_i_tech_require_driver_and_vehicle(self):
        for rec in self:
            if rec.sale_id:
                rec.i_tech_require_driver_and_vehicle = rec.sale_id.i_tech_require_driver_and_vehicle



    def button_validate(self):
        res = super().button_validate()
        for picking in self:
            if picking.picking_type_id.code != 'outgoing' or picking.location_id.usage != 'customer':
                continue

            if not picking.picking_type_id.i_tech_use_color_tag:
                continue
            else:
                for rec in picking.move_ids:
                    if not rec.i_tech_use_color_tag:
                        continue
                    if not rec.i_tech_color_tag_id:
                        raise ValidationError(_("Please select a Color Tag."))
        return res


    # def _action_done(self):
    #     res = super()._action_done()
    #     for move in self.move_ids:
    #         if move.sale_line_id and move.i_tech_color_tag_id:
    #             move.sale_line_id.i_tech_color_tag_id = move.i_tech_color_tag_id.id

    #     return res




    