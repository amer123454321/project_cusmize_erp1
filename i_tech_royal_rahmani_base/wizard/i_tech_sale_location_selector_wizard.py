
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError 

class ITechSaleLocationSelectorWizard(models.TransientModel):
    _name = 'i.tech.sale.location.selector.wizard'

    name = fields.Many2one('product.product','Product',required=True)
    sale_order_id = fields.Many2one('sale.order','Order')
    sale_order_line_id = fields.Many2one('sale.order.line','Line')
    product_uom_qty = fields.Float('Quantity',related='sale_order_line_id.product_uom_qty')

    line_ids = fields.One2many('i.tech.sale.location.selector.line.wizard','order_id','Lines')



    @api.onchange('name')
    def _onchange_product_id(self):
        """Populate lines with product quantities in all warehouses."""
        lines = []
        if self.name:
            # جلب كل المواقع المخزنية المخزنة على أنها 'internal'
            locations = self.env['stock.location'].search([('usage','=','internal'),('warehouse_id','=',self.sale_order_id.warehouse_id.id)])
            for location in locations:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', self.name.id),
                    ('location_id', '=', location.id)
                ])
                qty = sum(quants.mapped('quantity'))
                av_qty = sum(quants.mapped('available_quantity'))
                if qty > 0:
                    lines.append((0, 0, {
                        'order_id' : self.id,
                        'product_id' : self.name.id,
                        'location_id': location.id,
                        'on_hand' : qty,
                        'qty_available': av_qty,
                        'selected' : True if self.sale_order_line_id.i_tech_location_id.id == location.id else False

                    }))
        self.line_ids = lines


    
    def action_select(self):
        for rec in self:
            selected_lines = rec.line_ids.filtered(lambda l: l.selected)
            if not selected_lines:
                raise UserError("Please select a line before applying.")
            if len(selected_lines) > 1:
                raise UserError("Only one line can be selected. Please select a single line.")
            rec.sale_order_line_id.i_tech_location_id = selected_lines[0].location_id.id
            # rec.sale_order_line_id.write({
            #      'product_uom_qty' : rec.sale_order_line_id.product_uom_qty
            #  })
            # rec.sale_order_line_id._action_launch_stock_rule({})


class ITechSaleLocationSelectorLineWizard(models.TransientModel):
    _name = 'i.tech.sale.location.selector.line.wizard'

    order_id = fields.Many2one('i.tech.sale.location.selector.wizard','Order')


    product_id = fields.Many2one('product.product','Product',related='order_id.name')

    location_id = fields.Many2one('stock.location', string='Location')
    on_hand = fields.Float('On Hand')
    qty_available = fields.Float('Available Quantity')
    
    route_id = fields.Many2one('stock.route', string='Route')


    selected = fields.Boolean("Select")





    





