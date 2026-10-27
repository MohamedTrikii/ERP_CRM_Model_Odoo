# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _name = 'flowmerce.sale.order.line'
    _description = 'Sale Order Line'
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    order_id = fields.Many2one(
        'flowmerce.sale.order', string='Order Reference',
        required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, ondelete='restrict',
        domain=[('sale_ok', '=', True)],
    )
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(
        string='Quantity', required=True, default=1.0, digits='Product Unit of Measure',
    )
    product_uom = fields.Many2one(
        'uom.uom', string='Unit of Measure', ondelete='set null',
    )
    price_unit = fields.Float(
        string='Unit Price', required=True, digits='Product Price',
    )
    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    price_subtotal = fields.Float(
        string='Subtotal', compute='_compute_price_subtotal', store=True, digits='Product Price',
    )
    price_total = fields.Float(
        string='Total', compute='_compute_price_subtotal', store=True, digits='Product Price',
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Currency', store=True, readonly=True,
    )

    # ── Margin Fields ─────────────────────────────────────────────────────────
    cost_price = fields.Float(
        string='Cost Price', digits='Product Price', default=0.0,
        help="Unit cost used to compute line margin.",
    )
    margin = fields.Monetary(
        string='Margin', compute='_compute_margin', store=True,
        currency_field='currency_id',
    )
    margin_rate = fields.Float(
        string='Margin (%)', compute='_compute_margin', store=True, digits=(16, 2),
    )

    @api.depends('product_uom_qty', 'price_unit', 'discount', 'cost_price')
    def _compute_price_subtotal(self):
        for line in self:
            price = line.price_unit * (1.0 - line.discount / 100.0)
            subtotal = line.product_uom_qty * price
            line.price_subtotal = subtotal
            line.price_total = subtotal  # simplified: no taxes

    @api.depends('price_subtotal', 'cost_price', 'product_uom_qty')
    def _compute_margin(self):
        for line in self:
            cost_total = line.cost_price * line.product_uom_qty
            line.margin = line.price_subtotal - cost_total
            if line.price_subtotal:
                line.margin_rate = (line.margin / line.price_subtotal) * 100.0
            else:
                line.margin_rate = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.description_sale or self.product_id.name
            self.product_uom = self.product_id.uom_id
            self.price_unit = self.product_id.lst_price
            self.cost_price = self.product_id.standard_price
