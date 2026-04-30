# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _description = 'Purchase Order Line'
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one(
        'purchase.order', string='Order Reference',
        required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, ondelete='restrict',
        domain=[('purchase_ok', '=', True)],
    )
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(
        string='Quantity', required=True, default=1.0, digits='Product Unit of Measure',
    )
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', ondelete='set null')
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    price_subtotal = fields.Float(
        string='Subtotal', compute='_compute_price_subtotal', store=True, digits='Product Price',
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Currency', store=True, readonly=True,
    )

    @api.depends('product_uom_qty', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.price_unit * (1.0 - line.discount / 100.0)
            line.price_subtotal = line.product_uom_qty * price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.description_pickingin or self.product_id.name
            self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
            self.price_unit = self.product_id.standard_price
