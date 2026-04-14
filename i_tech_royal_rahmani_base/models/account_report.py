# -*- coding: utf-8 -*-

from odoo import fields, models, api, exceptions, _
from odoo.tools.image import UserError
from datetime import timedelta

class ITechAccountReport(models.Model):
    _inherit = 'account.report'




    def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):

        lines = super()._get_lines(options, all_column_groups_expression_totals, warnings)


        user = self.env.user
        if lines and not user.has_group('i_tech_royal_rahmani_base.i_tech_hide_account_group'):
            hide_accounts = self.env['account.account'].sudo().search([('i_tech_hide_account','=',True)]).ids
            filtered_lines = []
            for line in lines:
                account = line.get('account_id')
                line_id = line.get('id', '')

                # إذا كان السطر يحتوي على account_id مباشرة
                if account and account[0] in hide_accounts:
                    continue

                # إذا كان السطر إجمالي أو ليس له account_id، نحلل line_id
                parsed_ids = self._parse_line_id(line_id)  # نستخدم الدالة الرسمية
                hide_line = False
                for _, model, rec_id in parsed_ids:
                    if model == 'account.account' and rec_id in hide_accounts:
                        hide_line = True
                        break
                if hide_line:
                    continue

                filtered_lines.append(line)

            return filtered_lines
        return lines
    



    def get_options(self, previous_options):
        options = super().get_options(previous_options)
        if not self.env.user.has_group('i_tech_royal_rahmani_base.i_tech_hide_payable_group'):
            options['account_type'] = [
                account_type for account_type in options.get('account_type', [])
                if account_type['id'] not in ['trade_payable', 'non_trade_payable']
            ]

        return options
