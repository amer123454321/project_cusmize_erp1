# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager



class ITechDailyOrderPortal(CustomerPortal):

    # def _prepare_home_portal_values(self, counters):
    #     values = super()._prepare_home_portal_values(counters)
    #     partner = request.env.user.partner_id

    #     account_move_line = request.env['account.move.line'].sudo()
    #     values['project_count'] = account_move_line.search_count([('partner_id','=',partner.id),('parent_state', '=', 'posted')])

    #     return values
    
    @http.route(['/my/daily_order'], type='http',method=['POST','GET'], auth="user", website=True)
    def portal_my_i_tech_projects(self, **kwargs):
        partner = request.env.user.daily_order_partner_id
        block_update_order  = False
        values = False        
        if request.httprequest.method == 'POST':
            print('POST:')
            print(kwargs)
        else:        
            print('GET:')
            daily_order = request.env['i.tech.daily.order'].sudo().search([
                ('partner_id','=',partner.id),
                ('order_date', '=', fields.Date.today())
                ],limit=1)
            # daily_order = request.env['i.tech.daily.order'].sudo().search([],limit=1)
            if daily_order:
                if daily_order.order_state != 'draft':
                    block_update_order = True
                values = daily_order
  
        return request.render("i_tech_the_german_bakery_base.i_tech_portal_my_daily_order", {'daily_orders':values,'block_update_order':block_update_order,'page_name': "i_tech_daily_order_list_view"})


class DailyOrderController(http.Controller):

    @http.route('/daily_order/create', type='json', auth='public')
    def create_daily_order(self):


        user = request.env.user
        partner = request.env.user.daily_order_partner_id
        temp = request.env['i.tech.daily.order.template'].sudo().search([
                ('partner_ids','in',[partner.id])
                ],limit=1)
        message = f"Daily Order created by {user.name}!"
        line_vals = []
        for rec in temp.daily_order_line_ids:
            line_vals.append({
                'sequence' : rec.sequence,
                'product_id': rec.product_id.id,  
                'product_qty': 0,
                'price_unit': rec.price_unit,
            })
        order = request.env['i.tech.daily.order'].sudo().create({
            'name': 'Daily Order',
            'user_id': request.env.user.id,
            'order_date':  fields.Date.today(),
            'daily_order_line_ids': [(0, 0, line) for line in line_vals],
        }) 
           
        return {'status': 'success', 'message': message}
    



    @http.route('/daily_order/update', type='json', auth='user')
    def save_daily_order(self, **kwargs):
        # Logic for saving the daily order
        # Example: Save or confirm the current order
        updates = {data['line_id']: {'product_qty': data['quantity']} for data in kwargs['orderLines']}

        # Get all the ids from the updates dictionary
        record_ids = updates.keys()

        # Fetch all records in one query
        records = request.env['i.tech.daily.order.line'].sudo().browse(record_ids)

        # Prepare the write values for each record
        for record in records:
            if record.id in updates:
                record.write(updates[record.id])
        return {'message': 'No order found to save'}
    
