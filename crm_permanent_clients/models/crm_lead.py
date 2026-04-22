from odoo import _, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _promote_partner_to_permanent(self):
        """Ensure each lead has a linked partner and mark it as permanent client."""
        today = fields.Date.context_today(self)
        for lead in self:
            partner = lead.partner_id
            if not partner:
                # Create a partner from the lead's contact info, reusing the
                # standard CRM flow so emails/phones/addresses are copied.
                partner = lead._handle_partner_assignment(create_missing=True)
                if isinstance(partner, models.BaseModel):
                    lead.partner_id = partner
                else:
                    lead._create_customer()
                    partner = lead.partner_id
            if not partner:
                continue
            vals = {}
            if not partner.x_is_permanent_client:
                vals['x_is_permanent_client'] = True
            if not partner.x_permanent_since:
                vals['x_permanent_since'] = today
            if vals:
                partner.write(vals)
                partner.message_post(
                    body=_(
                        'Promoted to <b>Permanent Client</b> from CRM opportunity '
                        '<a href="#" data-oe-model="crm.lead" data-oe-id="%s">%s</a>.'
                    ) % (lead.id, lead.name or ''),
                )

    def write(self, vals):
        res = super().write(vals)
        # React when the stage changes to a "Won" stage.
        if 'stage_id' in vals:
            won_leads = self.filtered(
                lambda l: l.stage_id and l.stage_id.is_won and l.probability == 100
            )
            if won_leads:
                won_leads._promote_partner_to_permanent()
        return res

    def action_set_won_rainbowman(self):
        res = super().action_set_won_rainbowman()
        self._promote_partner_to_permanent()
        return res

    def action_mark_as_permanent_client(self):
        """Manual button: mark the lead's contact as a permanent client."""
        if not self:
            return False
        self._promote_partner_to_permanent()
        missing = self.filtered(lambda l: not l.partner_id)
        if missing:
            raise UserError(_(
                "The following leads have no contact to promote: %s"
            ) % ', '.join(missing.mapped('name')))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Permanent Client'),
                'message': _('Contact marked as a permanent client.'),
                'type': 'success',
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'res.partner',
                    'view_mode': 'form',
                    'res_id': self[:1].partner_id.id,
                },
            },
        }
