# -*- coding: utf-8 -*-
# from odoo import http


# class SizeOf(http.Controller):
#     @http.route('/size_of_mat/size_of_mat', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/size_of_mat/size_of_mat/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('size_of_mat.listing', {
#             'root': '/size_of_mat/size_of_mat',
#             'objects': http.request.env['size_of_mat.size_of_mat'].search([]),
#         })

#     @http.route('/size_of_mat/size_of_mat/objects/<model("size_of_mat.size_of_mat"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('size_of_mat.object', {
#             'object': obj
#         })

