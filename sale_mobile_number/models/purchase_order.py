# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mobile = fields.Char(
        string='Mobile',
        compute='_compute_mobile',
        store=True,
        readonly=False,
        help='Mobile number of the vendor',
    )

    @api.depends('partner_id')
    def _compute_mobile(self):
        for order in self:
            if order.partner_id:
                order.mobile = order.partner_id.mobile
            else:
                order.mobile = False
