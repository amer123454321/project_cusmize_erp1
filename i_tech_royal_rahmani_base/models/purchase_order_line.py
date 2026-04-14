# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _


class ITechPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sequence_number = fields.Integer(string='#',compute='_compute_sequence_number',help='Line Numbers')

    # i_tech_color_tag_id = fields.Many2one(
    #     'i.tech.product.color.tag',
    #     string="Color Tag",
    #     tracking=True
    # )

    # def _prepare_stock_moves(self, picking):
    #     moves = super()._prepare_stock_moves(picking)

    #     for mv in moves:
    #         if isinstance(mv, dict):
    #             mv['i_tech_color_tag_id'] = self.i_tech_color_tag_id.id
    #         else:
    #             mv.i_tech_color_tag_id = self.i_tech_color_tag_id.id

    #     return moves



    @api.depends('sequence', 'order_id')
    def _compute_sequence_number(self):
        """Function to compute line numbers"""
        for order in self.mapped('order_id'):
            sequence_number = 1
            for lines in order.order_line:
                if lines.display_type:
                    lines.sequence_number = sequence_number
                    sequence_number += 0
                else:
                    lines.sequence_number = sequence_number
                    sequence_number += 1