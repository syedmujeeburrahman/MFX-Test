from odoo import fields, models


class CountryCallingGuide(models.Model):
    _name = 'x_erp.country_calling_guide'
    _description = '195 Countries Cold Calling Guide'
    _order = 'x_erp_ist_sort_order asc, x_erp_call_sequence asc'

    x_erp_country_name = fields.Char(string='Country Name', required=True)
    x_erp_ist_call_group = fields.Char(string='IST Call Time Slot')
    x_erp_ist_sort_order = fields.Float(string='IST Sort Order')
    x_erp_call_sequence = fields.Integer(string='Call Order')
    x_erp_utc_offset = fields.Char(string='UTC Offset')
    x_erp_best_ist_time = fields.Char(string='Best Time to Call (IST)')
    x_erp_country_local_time = fields.Char(string='Country Local Time')
    x_erp_calling_notes = fields.Text(string='Notes')
