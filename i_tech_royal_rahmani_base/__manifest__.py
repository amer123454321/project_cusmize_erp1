# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ITech Royal Rahmani Base',
    'version': '1.0',
    'summary': 'ITech Royal Rahmani Base.',
    'depends': ['base','web','product','account', 'purchase','sale_stock','sale','stock'],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        'security/product_product_views.xml',
        'security/product_template_views.xml',
        'security/purchase.xml',
        'security/partner_type.xml',
        "views/account_payment_register.xml",
        "views/account_account.xml",
        "views/account_move_line.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/i_tech_account_payment.xml",
        "views/product_template.xml",
        "views/purchase_order.xml",
        "views/res_company.xml",
        "views/res_currency.xml",
        "views/res_partner.xml",
        "views/res_users.xml",
        "views/sale_order.xml",
        "views/product_pricelist.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
        "views/stock_warehouse.xml",
        "views/i_tech_location_tag.xml",
        "views/i_tech_product_color_tag.xml",
        "views/i_tech_partner_type.xml",
        "views/snake_game_action.xml",
        "views/i_tech_menuitem.xml",
        "wizard/i_tech_sale_location_selector_wizard.xml",
        "wizard/i_tech_stock_move_location_selector_wizard.xml",

        
    ],
    'assets': {
        'web.assets_backend': [
            'i_tech_royal_rahmani_base/static/src/js/snake_game_logic.js',
            'i_tech_royal_rahmani_base/static/src/js/snake_game_action.js',
            'i_tech_royal_rahmani_base/static/src/scss/snake_game.scss',
            'i_tech_royal_rahmani_base/static/src/**/*.xml',
        ],
        'web.qunit_suite_tests': [
            'i_tech_royal_rahmani_base/static/tests/snake_game_logic_tests.js',
        ],
    },
    'auto_install': False,
    'application': True,
    'installable': True,
}
