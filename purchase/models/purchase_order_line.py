from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _description = 'Purchase Order Line'

    order_id = fields.Many2one('purchase.order', string='Order Reference', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit
