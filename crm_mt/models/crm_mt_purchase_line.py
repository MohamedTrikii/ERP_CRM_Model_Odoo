from odoo import models, fields

class CrmMtPurchaseLine(models.Model):
    _name = 'crm.mt.purchase.line'
    _description = 'CRM_MT Purchase Order Line'

    order_id = fields.Many2one('crm.mt.purchase', string='Purchase Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Float('Unit Price', default=0.0)
    price_subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
