# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.osv import expression
from odoo.tools.image import UserError


class ITechStockMove(models.Model):
    _inherit = 'stock.move'

    i_tech_color_tag_id = fields.Many2one(
        'i.tech.product.color.tag',
        string="Color Tag",
        tracking=True
    )



    i_tech_use_color_tag = fields.Boolean(string='Use Color Tag',compute='_compute_i_tech_use_color_tag',store=True)

    i_tech_location_tag_ids = fields.Many2many(
        'i.tech.location.tag.line',
        string='Location Tags',
        compute='_compute_location_tags',
        store=False
    )



    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()

        analytic_distribution = False
        if self.sale_line_id:  # إذا مرتبط ببيع
            analytic_distribution = self.sale_line_id.analytic_distribution

        elif self.purchase_line_id:  # إذا مرتبط بمشتريات
            analytic_distribution = self.purchase_line_id.analytic_distribution

        else:
            warehouse_id = self.env['stock.valuation.layer'].sudo().browse(svl_id).warehouse_id
            if warehouse_id.i_tech_analytic_account:
                analytic_distribution = {warehouse_id.i_tech_analytic_account.id: 100.00}
            
        # استدعاء الدالة الأصلية لإنشاء قيود الحساب
        move_vals = super()._prepare_account_move_vals(
            credit_account_id,
            debit_account_id,
            journal_id,
            qty,
            description,
            svl_id,
            cost
        )

        # إضافة الحساب التحليلي إلى كل سطر إذا تم تحديده
        if analytic_distribution:
            for line in move_vals['line_ids']:
                line_dict = line[2]  # line format is (0, 0, {vals})
                line_dict['analytic_distribution'] = analytic_distribution

        return move_vals
    


    def write(self, vals):
        for rec in self:
            if 'location_id' in vals and self.sale_line_id:
                    if not self.env.context.get('skip_write_location'):
                        i_tech_location_id = vals['location_id']
                        rec.i_tech_change_location(i_tech_location_id)



            res = super(ITechStockMove, self).write(vals)


            return res




    def i_tech_change_location(self,i_tech_location_id):
        for rec in self:   
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
                    rec.sale_line_id.with_context(skip_write_location=True).write({
                        'i_tech_location_id': i_tech_location_id,
                    })

                    rec.rule_id = stock_rule.id
                else:
                    raise UserError("No suitable stock rule found for this location.")

    @api.depends('product_id', 'location_id','location_dest_id')
    def _compute_location_tags(self):
        for move in self:
            location_id = False
            if move.location_id.usage == 'internal':
                location_id = move.location_id
            elif move.location_dest_id.usage == 'internal':
                location_id = move.location_dest_id

            if move.product_id and location_id:
                tags = self.env['i.tech.location.tag.line'].search([
                    ('id', 'in', move.product_id.i_tech_location_tag_ids.tag_ids.ids),
                    ('location_id', '=', location_id.id)
                ])
                move.i_tech_location_tag_ids = tags
            else:
                move.i_tech_location_tag_ids = False



    @api.depends('product_id','picking_type_id')
    def _compute_i_tech_use_color_tag(self):
        for rec in self:
            i_tech_use_color_tag = False
            if rec.product_id.i_tech_use_color_tag and rec.picking_type_id.i_tech_use_color_tag:
                i_tech_use_color_tag = True
            else:
                i_tech_use_color_tag = False
            
            rec.i_tech_use_color_tag = i_tech_use_color_tag



    @api.onchange('i_tech_color_tag_id')
    def onchange_i_tech_color_tag_id(self):
        for rec in self:
            if rec.sale_line_id:
                rec.sale_line_id.i_tech_color_tag_id = rec.i_tech_color_tag_id.id






    def action_open_location_selector_wizard(self):
        self.ensure_one()  
        action = self.env["ir.actions.actions"]._for_xml_id("i_tech_royal_rahmani_base.action_i_tech_stock_move_location_selector_wizard")
        action['context'] = {
            'default_picking_id': self.picking_id.id,
            'default_name':self.product_id.id,
            'default_stock_move_id':self.id,
            }
        return action
        



    def _get_analytic_distribution(self):
        for rec in self:
            distribution = False
            if rec.sale_line_id:
                analytic_distribution = rec.sale_line_id.analytic_distribution
                if analytic_distribution:
                   distribution = analytic_distribution  
        return distribution or super()._get_analytic_distribution()






class ITechStockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super()._get_custom_move_fields()
        fields.append('i_tech_color_tag_id')
        fields.append('picking_id')
        return fields
    

    def _get_stock_move_values(
        self, product_id, product_qty, product_uom,
        location_dest_id, name, origin, company_id, values
    ):
        # استدعاء السوبر
        move_values = super()._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_dest_id, name, origin, company_id, values
        )

        # إضافة picking_id إذا كان موجوداً في values
        if values.get('picking_id'):
            move_values['picking_id'] = values['picking_id']

        return move_values
    
    
    
class ITechProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    def _prepare_procurement_values(self, *args, **kwargs):
        vals = super()._prepare_procurement_values(*args, **kwargs)
        if self.sale_id and self.sale_id.order_line:
            vals['i_tech_color_tag_id'] = self.sale_id.order_line[0].i_tech_color_tag_id.id
        return vals
    



    @api.model
    def _get_rule_domain(self, location, values):
        domain = super()._get_rule_domain(location, values)
        if domain and domain[0] == '&':
            domain = domain[1:]
        if values.get('location_src_id'):
            domain.insert(0, ('location_src_id', '=', values['location_src_id']))
        return domain

    # @api.model
    # def _search_rule(self, route_ids, packaging_id, product_id, warehouse_id, domain):
    

    #     res = super()._search_rule(
    #         route_ids,
    #         packaging_id,
    #         product_id,
    #         warehouse_id,
    #         domain
    #     )

    #     Rule = self.env['stock.rule']
    #     if not res and warehouse_id:
    #         warehouse_routes = warehouse_id.route_ids
    #         if warehouse_routes:
    #             res = Rule.search(expression.AND([[('route_id', 'in', warehouse_routes.ids)], domain]), order='route_sequence, sequence', limit=1)





    #     return res 
