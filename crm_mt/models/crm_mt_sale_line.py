# -*- coding: utf-8 -*-
"""
Optimized CRM MT Sale Order Line model for Odoo 19: performance, scalability, maintainability.
"""
from odoo import models, fields, api


class CrmMtSaleLine(models.Model):
    """
    CRM MT Sale Order Line
    Optimized for performance and scalability.
    """
    _name = 'crm.mt.sale.line'
    _description = 'CRM MT Sale Order Line'
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Sequence', default=10, index=True)
    order_id = fields.Many2one(
        'crm.mt.sale', string='Sale Order', required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one(
        'product.product', string='Product', required=True, ondelete='restrict', index=True,
    )
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(
        string='Quantity', required=True, default=1.0, digits='Product Unit of Measure',
    )
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', ondelete='set null', index=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')
    price_subtotal = fields.Float(
        string='Subtotal', compute='_compute_price_subtotal', store=True, digits='Product Price',
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id', string='Currency', store=True, readonly=True,
    )

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_price_subtotal(self):
        """Compute subtotal efficiently."""
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill fields from product selection."""
        if self.product_id:
            self.name = self.product_id.description_sale or self.product_id.name
            self.product_uom = self.product_id.uom_id
            self.price_unit = self.product_id.lst_price
