# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'


    def _check_user_invoice_lock(self):


        user = self.env.user

        if not user.invoice_lock_enabled:
            return

        lock_days = user.invoice_lock_days or 0

        if lock_days <= 0:
            return

        limit_date = fields.Date.context_today(self) - timedelta(days=lock_days)

        for move in self:

            if move.move_type not in (
                'out_invoice',
                'in_invoice',
                'out_refund',
                'in_refund',
            ):
                continue

            if move.invoice_date and move.invoice_date < limit_date:
                raise UserError(_(
                    "⛔ You are not allowed to modify or reopen this invoice.\n\n"
                    "Invoice Date: %s\n"
                    "Allowed Modification Period: %s day(s)\n\n"
                    "Please contact your manager."
                ) % (move.invoice_date, lock_days))

    #
    # def write(self, vals):
    #     return super().write(vals)

    def unlink(self):
        self._check_user_invoice_lock()
        return super().unlink()

    # ==========================================================
    # Prevent Reset to Draft
    # ==========================================================
    def button_draft(self):
        self._check_user_invoice_lock()
        return super().button_draft()
