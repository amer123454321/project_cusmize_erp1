# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import float_compare


class ITechSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    # _inherit = ['mail.thread', 'mail.activity.mixin']


    sequence_number = fields.Integer(string='#',compute='_compute_sequence_number',store=True,help='Line Numbers')

    i_tech_color_tag_id = fields.Many2one('i.tech.product.color.tag',string="Color Tag",tracking=True)


    i_tech_location_id = fields.Many2one('stock.location','Location',compute="_compute_i_tech_location_id",store=True,readonly=False,tracking=True)
    

    i_tech_use_sale_location_id = fields.Boolean('Use Sale Location',related='company_id.i_tech_use_sale_location_id')


    i_tech_free_product = fields.Boolean('Free',tracking=True)



    @api.onchange('i_tech_free_product')
    def onchange_i_tech_free_product(self):
        for rec in self:
            if rec.i_tech_free_product:
                rec.price_unit = 0
            else:
                if rec.product_id and rec.order_id.pricelist_id:
                    rec.price_unit = rec.order_id.pricelist_id._get_product_price(
                        rec.product_id, rec.product_uom_qty or 1.0, rec.order_id.partner_id
                    )


    @api.onchange('product_id')
    def onchange_or_create_product_id(self):
        for rec in self:
            i_tech_analytic_account = rec.order_id.i_tech_analytic_account
            if i_tech_analytic_account:
                rec.analytic_distribution = {i_tech_analytic_account.id: 100.00}




    @api.depends('route_id','product_id')
    def _compute_i_tech_location_id(self):
        for rec in self:
            i_tech_location_id = False
            if rec.route_id:
                stock_rule = self.env['stock.rule'].sudo().search([
                    ('active','=',True),
                    ('procure_method','=','make_to_stock'),
                    ('action','=','pull'),
                    ('route_id','=',rec.route_id.id),
                    ('location_dest_id.usage','=','customer'),
                    ('picking_type_id.code','=','outgoing'),
                    ('route_id.sale_selectable', '=', True)
                ],limit=1)
                i_tech_location_id = stock_rule.location_src_id.id
            else:
                if rec.order_id.warehouse_id:
                    i_tech_location_id = rec.order_id.warehouse_id.lot_stock_id.id

            rec.i_tech_location_id = i_tech_location_id
    





    def _prepare_procurement_values(self, group_id=False):
        vals = super()._prepare_procurement_values(group_id)

        vals['i_tech_color_tag_id'] = self.i_tech_color_tag_id.id

        vals.update({'location_src_id': self.i_tech_location_id.id if self.i_tech_location_id else False})

        if self.order_id:  # self = sale.order.line
            pickings = self.order_id.picking_ids.filtered(
                lambda p: p.state not in ('cancel', 'done')
            ).sorted(key=lambda p: p.id, reverse=True)

            if pickings:
                picking = pickings[0]
                vals['picking_id'] = picking.id
            else:
                picking_type = self.order_id.warehouse_id.out_type_id
                picking_vals = {
                    'picking_type_id': picking_type.id,
                    'partner_id': self.order_id.partner_shipping_id.id,
                    'origin': self.order_id.name,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': self.order_id.partner_shipping_id.property_stock_customer.id,
                    'company_id': self.order_id.company_id.id,
                    'sale_id': self.order_id.id,
                }

                picking = self.env['stock.picking'].create(picking_vals)

                self.order_id.picking_ids = [(4, picking.id)]

                vals['picking_id'] = picking.id


        
        return vals
    





    def _prepare_stock_moves(self, picking):
        moves = super()._prepare_stock_moves(picking)
        for mv in moves:
            if isinstance(mv, dict):
                mv['i_tech_color_tag_id'] = self.i_tech_color_tag_id.id
            else:
                mv.i_tech_color_tag_id = self.i_tech_color_tag_id.id
        return moves


    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.move_ids:
                color_tag = next((m.i_tech_color_tag_id.id for m in line.move_ids if m.i_tech_color_tag_id), False)
                if color_tag and not line.i_tech_color_tag_id:
                    line.write({'i_tech_color_tag_id': color_tag})
                if line.move_ids.location_id:
                    line.write({'i_tech_location_id': line.move_ids.location_id.id})


            if line.order_id.i_tech_analytic_account:
                analytic_distribution = {line.order_id.i_tech_analytic_account.id: 100.00}
                line.write({'analytic_distribution': analytic_distribution})         
        return lines


    @api.onchange('i_tech_color_tag_id')
    def onchange_i_tech_color_tag_id(self):
        for rec in self:
            for move in rec.move_ids:
                move.i_tech_color_tag_id = rec.i_tech_color_tag_id.id



    # @api.onchange('i_tech_location_id')
    # def onchange_i_tech_location_id(self):
    #     for rec in self:
    #         move = rec.move_ids.filtered(
    #             lambda m: m.picking_id
    #             and m.picking_id.state not in ('cancel', 'done')
    #         ).sorted(
    #             key=lambda m: m.picking_id.id,
    #             reverse=True
    #         )[:1]

    #         if move:
                
    #             stock_rule = self.env['stock.rule'].sudo().search([
    #                 ('active','=',True),
    #                 ('procure_method','=','make_to_stock'),
    #                 ('action','=','pull'),
    #                 ('location_src_id','=',rec.i_tech_location_id.id),
    #                 ('location_dest_id.usage','=','customer'),
    #                 ('picking_type_id.code','=','outgoing'),
    #                 ('route_id.sale_selectable', '=', True)
    #             ],limit=1)
    #             route_id = stock_rule.route_id
    #             if route_id:
    #                 move.location_id = rec.i_tech_location_id.id 
    #                 move.rule_id = stock_rule.id



    def write(self, vals):
        for rec in self:
            if 'i_tech_location_id' in vals:
                    if not self.env.context.get('skip_write_location'):
                        i_tech_location_id = vals['i_tech_location_id']
                        rec.i_tech_change_location(i_tech_location_id)

                            
            res = super(ITechSaleOrderLine, self).write(vals)

            
            if 'product_uom_qty' in vals:
                new_qty = vals['product_uom_qty']

                if float_compare(
                    new_qty,
                    rec.qty_delivered,
                    precision_rounding=rec.product_uom.rounding
                ) == 0:

                    moves = rec.move_ids.filtered(
                        lambda m: m.state not in ('cancel', 'done')
                    )

                    moves.write({'product_uom_qty': 0})
            return res     



    def i_tech_change_location(self,i_tech_location_id):
        for rec in self:   
            move = rec.move_ids.filtered(
                    lambda m: m.picking_id and m.picking_id.state not in ('cancel', 'done')
                ).sorted(key=lambda m: m.picking_id.id, reverse=True)[:1]

            if move:
                stock_rule = self.env['stock.rule'].sudo().search([
                    ('active','=',True),
                    ('procure_method','=','make_to_stock'),
                    ('action','=','pull'),
                    ('location_src_id','=',i_tech_location_id),
                    ('location_dest_id.usage','=','customer'),
                    ('picking_type_id.code','=','outgoing'),
                    ('route_id.sale_selectable', '=', True)
                ], limit=1)

                route_id = stock_rule.route_id if stock_rule else False
                if route_id:
                    move.with_context(skip_write_location=True).write({
                        'location_id': i_tech_location_id,
                        'rule_id': stock_rule.id,
                    })









    def action_open_location_selector_wizard(self):
        self.ensure_one()  
        action = self.env["ir.actions.actions"]._for_xml_id("i_tech_royal_rahmani_base.action_i_tech_sale_location_selector_wizard")
        action['context'] = {
            'default_sale_order_id': self.order_id.id,
            'default_name':self.product_id.id,
            'default_sale_order_line_id':self.id,
            }
        return action
        



        
    # ----------------------------
    # Compute sequence numbers
    # ----------------------------
    @api.depends('sequence', 'order_id', 'display_type')
    def _compute_sequence_number(self):
        # for order in self.mapped('order_id'):
            self.sequence_number = 1
            # for line in order.order_line:
            #     line.sequence_number = sequence_number
            #     if not line.display_type:
            #         sequence_number += 1
