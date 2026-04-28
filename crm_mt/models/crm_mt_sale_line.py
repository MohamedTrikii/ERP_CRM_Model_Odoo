from odoo import models, fields

class CrmMtSaleLine(models.Model):
    _name = 'crm.mt.sale.line'
    _description = 'CRM_MT Sale Order Line'

    order_id = fields.Many2one('crm.mt.sale', string='Sale Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Float('Unit Price', default=0.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
