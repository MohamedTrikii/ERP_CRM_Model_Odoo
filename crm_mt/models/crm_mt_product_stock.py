# -*- coding: utf-8 -*-
"""
CRM_TRIKI ERP — Product Stock simulation model (Odoo 19).
Used when no native stock module is installed.
Tracks availability, triggers auto-purchase alerts.
"""
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrmMtProductStock(models.Model):
    """
    Simulated stock tracking per product.
    Provides qty_available, qty_reserved, qty_ordered and low-stock alerts.
    """
    _name = 'crm.mt.product.stock'
    _description = 'Product Stock (CRM_TRIKI ERP)'
    _rec_name = 'product_id'
    _order = 'product_id'

    _product_uniq = models.Constraint(
        'UNIQUE(product_id)',
        'Stock entry already exists for this product.',
    )
    _qty_available_positive = models.Constraint(
        'CHECK(qty_available >= 0)',
        'Available quantity cannot be negative.',
    )

    # ── Core ──────────────────────────────────────────────────────────────────
    product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        ondelete='cascade', index=True,
    )
    product_name = fields.Char(
        related='product_id.name', string='Product Name', readonly=True,
    )
    category_id = fields.Many2one(
        related='product_id.categ_id', string='Category', store=True, readonly=True,
    )
    uom_id = fields.Many2one(
        related='product_id.uom_id', string='Unit', store=True, readonly=True,
    )

    # ── Quantities ────────────────────────────────────────────────────────────
    qty_available = fields.Float(
        string='Qty Available', default=0.0,
        help="Current physical stock on hand.",
    )
    qty_reserved = fields.Float(
        string='Qty Reserved', default=0.0,
        help="Quantity reserved for confirmed sale orders.",
    )
    qty_ordered = fields.Float(
        string='Qty On Order', default=0.0,
        help="Quantity in pending purchase orders.",
    )
    qty_min_alert = fields.Float(
        string='Min Alert Qty', default=5.0,
        help="When qty_available drops below this threshold, a low-stock alert is raised.",
    )
    qty_to_reorder = fields.Float(
        string='Qty to Reorder', default=10.0,
        help="Default quantity to order when auto-purchase is triggered.",
    )

    # ── Computed ──────────────────────────────────────────────────────────────
    qty_net = fields.Float(
        string='Net Available', compute='_compute_qty_net', store=True,
        help="qty_available - qty_reserved",
    )
    stock_status = fields.Selection([
        ('ok', 'OK'),
        ('low', 'Low Stock'),
        ('critical', 'Critical — Reorder Now'),
        ('out', 'Out of Stock'),
    ], string='Stock Status', compute='_compute_stock_status', store=True)

    # ── Constraints ───────────────────────────────────────────────────────────
    @api.constrains('qty_reserved')
    def _check_reserved(self):
        for rec in self:
            if rec.qty_reserved > rec.qty_available:
                raise ValidationError(
                    f'Reserved quantity ({rec.qty_reserved}) cannot exceed '
                    f'available quantity ({rec.qty_available}) for "{rec.product_name}".'
                )

    # ── Computed Methods ──────────────────────────────────────────────────────
    @api.depends('qty_available', 'qty_reserved')
    def _compute_qty_net(self):
        for rec in self:
            rec.qty_net = rec.qty_available - rec.qty_reserved

    @api.depends('qty_net', 'qty_min_alert')
    def _compute_stock_status(self):
        for rec in self:
            net = rec.qty_net
            alert = rec.qty_min_alert or 0
            if net <= 0:
                rec.stock_status = 'out'
            elif net < (alert * 0.5):
                rec.stock_status = 'critical'
            elif net < alert:
                rec.stock_status = 'low'
            else:
                rec.stock_status = 'ok'

    # ── Stock Movement Helpers ─────────────────────────────────────────────────
    def add_stock(self, qty):
        """Increase available quantity (e.g. after reception)."""
        self.ensure_one()
        if qty <= 0:
            raise ValidationError('Quantity to add must be positive.')
        self.qty_available += qty
        self.qty_ordered = max(0.0, self.qty_ordered - qty)
        _logger.info('Stock +%s for %s → %s', qty, self.product_name, self.qty_available)

    def reserve_stock(self, qty):
        """Reserve quantity for a sale order."""
        self.ensure_one()
        if qty > self.qty_net:
            raise ValidationError(
                f'Cannot reserve {qty} units of "{self.product_name}". '
                f'Net available: {self.qty_net}.'
            )
        self.qty_reserved += qty

    def release_stock(self, qty):
        """Release reservation (e.g. on cancellation)."""
        self.ensure_one()
        self.qty_reserved = max(0.0, self.qty_reserved - qty)

    # ── Low Stock Alert ───────────────────────────────────────────────────────
    def check_low_stock(self):
        """Post chatter message and return records that need reordering."""
        low = self.filtered(lambda s: s.stock_status in ('low', 'critical', 'out'))
        for rec in low:
            rec.message_post(
                body=(
                    f'⚠️ <b>CRM_TRIKI Stock Alert</b>: "{rec.product_name}" — '
                    f'Net available: {rec.qty_net} {rec.uom_id.name or "units"} '
                    f'(status: {rec.stock_status}). Reorder threshold: {rec.qty_min_alert}.'
                ),
                subject='Low Stock Alert — CRM_TRIKI ERP',
            )
        return low

    # ── Auto-Trigger Purchase ─────────────────────────────────────────────────
    def auto_trigger_purchase(self):
        """
        Auto-create a purchase order line for critically low products.
        Looks for the cheapest supplier on the product.
        Requires the flowmerce_purchase module; suppliers come from product.seller_ids
        when Odoo's purchase app provides it.
        """
        if 'flowmerce.purchase.order' not in self.env:
            _logger.warning('CRM_TRIKI Stock: flowmerce_purchase is not installed. Skipping auto-PO.')
            return
        for rec in self.filtered(lambda s: s.stock_status in ('critical', 'out')):
            product = rec.product_id
            # Find default supplier
            sellers = getattr(product, 'seller_ids', False)
            seller = sellers and sellers[0]
            if not seller:
                _logger.warning(
                    'CRM_TRIKI Stock: no supplier configured for %s. Skipping auto-PO.',
                    product.name,
                )
                continue
            # Create PO
            po = self.env['flowmerce.purchase.order'].create({
                'partner_id': seller.partner_id.id,
                'auto_order_flag': True,
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': rec.qty_to_reorder,
                    'product_uom': (getattr(product, 'uom_po_id', False) or product.uom_id).id,
                    'price_unit': seller.price or product.standard_price,
                })],
            })
            rec.qty_ordered += rec.qty_to_reorder
            rec.message_post(
                body=(
                    f'🛒 Auto-PO created: <a href="/odoo/purchase-orders/{po.id}">'
                    f'{po.name}</a> for {rec.qty_to_reorder} × {product.name}.'
                ),
                subject='Auto-Purchase Created — CRM_TRIKI ERP',
            )
            _logger.info('CRM_TRIKI: auto-PO %s created for %s.', po.name, product.name)

    # ── Cron Entry Point ─────────────────────────────────────────────────────
    @api.model
    def cron_check_low_stock(self):
        """Cron job: scan all stock records for low/critical/out status."""
        all_stocks = self.search([])
        all_stocks._compute_stock_status()
        low = all_stocks.filtered(lambda s: s.stock_status in ('low', 'critical', 'out'))
        low.check_low_stock()
        critical = low.filtered(lambda s: s.stock_status in ('critical', 'out'))
        if critical:
            critical.auto_trigger_purchase()
        _logger.info(
            'CRM_TRIKI Stock Cron: %d low, %d critical/out of %d total.',
            len(low), len(critical), len(all_stocks),
        )
