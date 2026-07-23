from odoo import fields, models


class ProspectDuplicateWizard(models.TransientModel):
    _name = 'x_erp.prospect_duplicate_wizard'
    _description = 'Prospect Duplicate Warning'

    prospect_id = fields.Many2one('x_erp.prospect', required=True, readonly=True)
    duplicate_id = fields.Many2one('x_erp.prospect', string='Existing Prospect', required=True)
    company_name = fields.Char(related='duplicate_id.name', readonly=True)
    salesperson_id = fields.Many2one(related='duplicate_id.user_id', readonly=True)
    current_status = fields.Selection(related='duplicate_id.status', readonly=True)
    last_contact_date = fields.Date(related='duplicate_id.last_contact_date', readonly=True)
    duplicate_summary = fields.Text(related='prospect_id.duplicate_warning', readonly=True)

    def action_open_existing(self):
        self.ensure_one()
        self.prospect_id._create_audit_log(
            'duplicate',
            '<p>Opened existing duplicate prospect: %s</p>' % self.duplicate_id.display_name,
        )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Existing Prospect',
            'res_model': 'x_erp.prospect',
            'view_mode': 'form',
            'res_id': self.duplicate_id.id,
        }

    def action_continue_anyway(self):
        self.ensure_one()
        self.prospect_id.write({'duplicate_reviewed': True})
        self.prospect_id._create_audit_log(
            'duplicate',
            '<p>Duplicate warning reviewed and user continued with this prospect.</p>',
        )
        return {'type': 'ir.actions.act_window_close'}
