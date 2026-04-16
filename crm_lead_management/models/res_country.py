from odoo import models, api
from odoo.osv import expression


class ResCountry(models.Model):
    _inherit = 'res.country'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """Enhanced country search with fuzzy matching fallback.

        If the standard search finds no results, try matching using
        overlapping 3-character substrings from the search term.
        This handles common misspellings like 'nather' -> 'Netherlands'
        because substrings 'the' and 'her' still match.
        """
        res = super().name_search(name=name, args=args, operator=operator, limit=limit)
        if res or not name or len(name) < 3 or operator not in ('ilike', 'like', '=ilike'):
            return res

        # Fuzzy fallback: extract overlapping 3-char substrings and
        # search for any country whose name matches at least one.
        trigrams = [name[i:i + 3] for i in range(len(name) - 2)]

        # Build OR domain in Odoo Polish notation
        or_domain = ['|'] * (len(trigrams) - 1)
        for tri in trigrams:
            or_domain.append(('name', 'ilike', tri))

        domain = expression.AND([or_domain, args or []])
        records = self.search_fetch(domain, ['display_name'], limit=limit)
        return [(record.id, record.display_name) for record in records.sudo()]
