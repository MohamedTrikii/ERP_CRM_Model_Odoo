from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_ids = fields.One2many('sale.order', 'partner_id', string='Sales Orders')
