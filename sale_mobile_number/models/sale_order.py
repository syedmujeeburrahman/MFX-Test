# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mobile = fields.Char(
        string='Mobile',
        compute='_compute_mobile',
        store=True,
        readonly=False,
        help='Mobile number of the customer',
    )

    x_description = fields.Text(
        string='Description',
        help='Additional description or notes for this quotation/order',
    )

    @api.depends('partner_id')
    def _compute_mobile(self):
        for order in self:
            if order.partner_id:
                order.mobile = order.partner_id.mobile
            else:
                order.mobile = False
