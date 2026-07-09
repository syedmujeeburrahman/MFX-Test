from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_prospect_id = fields.Many2one(
        'x_erp.prospect',
        string='Source Prospect',
        copy=False,
        index=True,
    )

    def action_view_source_prospect(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Source Prospect',
            'res_model': 'x_erp.prospect',
            'view_mode': 'form',
            'res_id': self.x_prospect_id.id,
        }
