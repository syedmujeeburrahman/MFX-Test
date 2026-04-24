from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_mobile = fields.Char(
        string='Mobile',
        compute='_compute_x_mobile',
        store=True,
        readonly=False,
        help='Customer mobile number. Defaulted from the customer record and '
             'editable on the order.',
    )

    @api.depends('partner_id')
    def _compute_x_mobile(self):
        for order in self:
            if order.partner_id and not order.x_mobile:
                order.x_mobile = order.partner_id.mobile or order.partner_id.phone or False
            elif not order.partner_id:
                order.x_mobile = False
