from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    flowmerce_sale_order_ids = fields.One2many('flowmerce.sale.order', 'partner_id', string='Sales Orders')
