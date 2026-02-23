# -*- coding: utf-8 -*-
{
    'name': "Project cusmize erp",

    'summary': "Custom module for invoice locks, customer levels, credit limits, and sales profit",
    'description': """
            - Lock invoices after certain days per user
            - Customer levels: normal, VIP, dealer
            - Max discount per customer level
            - Credit limit validation
            - Allowed currencies per customer
            - Sales Order profit calculation
            - Inventory check before confirm
            - Discount approval workflow
        """,

     'author': 'Amer Sultan',
    'company': 'ERP Solutions',


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_accountant','web','social_media', 'sale', 'account', 'sale_management'],


    # always loaded
    'data': [
        # 'views/views.xml',
        # 'account_move_line_views.xml',
        'views/account_move_line.xml',
        'views/custmize_account_move_account_lock.xml',
        'views/custmize_res_user_Invoice_lock.xml',
        'views/res_partner_form.xml',
        'views/custmize_res_company.xml',

        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

