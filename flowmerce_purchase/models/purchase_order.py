# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _name = 'flowmerce.purchase.order'
    _description = 'Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    # -- Identification
    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'),
    )

    # -- Partners
    partner_id = fields.Many2one(
        'res.partner', string='Supplier', required=True, tracking=True, index=True,
    )
    partner_email = fields.Char(related='partner_id.email', string='Supplier Email', readonly=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Supplier Phone', readonly=True)

    # -- Dates
    date_order = fields.Datetime(
        string='Order Date', required=True, default=fields.Datetime.now, tracking=True,
    )
    date_approve = fields.Datetime(string='Confirmation Date', readonly=True, copy=False)

    # -- Status
    state = fields.Selection([
        ('draft', 'Request for Quotation'),
        ('sent', 'RFQ Sent'),
        ('purchase', 'Purchase Order'),
        ('received', 'Received'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    invoice_status = fields.Selection([
        ('no', 'Nothing to Invoice'),
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Fully Invoiced'),
    ], string='Invoice Status', compute='_compute_invoice_status',
       store=True, readonly=True, default='no')

    # -- Order Lines
    order_line = fields.One2many(
        'flowmerce.purchase.order.line', 'order_id', string='Order Lines', copy=True,
    )

    # -- Amounts
    amount_untaxed = fields.Monetary(
        string='Untaxed Amount', store=True, compute='_compute_amounts', tracking=True,
    )
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(
        string='Total', store=True, compute='_compute_amounts', tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.company.currency_id,
    )

    # -- Purchase Info
    user_id = fields.Many2one(
        'res.users', string='Buyer', default=lambda self: self.env.user, tracking=True,
    )
    team_id = fields.Many2one('crm.mt.team', string='Buyer Team', tracking=True)
    note = fields.Text(string='Terms and Conditions')

    # -- Analytics
    priority = fields.Selection([
        ('0', 'Normal'), ('1', 'Important'), ('2', 'Urgent'),
    ], string='Priority', index=True, default='0', tracking=True)
    expected_amount = fields.Monetary(
        string='Expected Amount', currency_field='currency_id', tracking=True, default=0.0,
    )
    probability = fields.Float(string='Success Probability (%)', default=0.0, tracking=True)
    description = fields.Html(string='Description')

    # -- Flowmerce: Supplier Intelligence
    supplier_score = fields.Float(
        string='Supplier Score', compute='_compute_supplier_score', store=True,
        digits=(16, 1), help="Flowmerce AI score (0–100) for this supplier.",
    )
    delay_risk = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], string='Delivery Risk', compute='_compute_delay_risk', store=True, tracking=True)
    auto_order_flag = fields.Boolean(
        string='Auto-Order', default=False, tracking=True,
        help="If enabled, this PO can be auto-confirmed when stock is critically low.",
    )
    expected_delivery_date = fields.Date(
        string='Expected Delivery', tracking=True, index=True,
    )
    actual_delivery_date = fields.Date(
        string='Actual Delivery', tracking=True,
    )

    # -- Computed Methods

    @api.depends('order_line.price_subtotal')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            order.amount_untaxed = amount_untaxed
            order.amount_tax = 0.0
            order.amount_total = amount_untaxed
            if not order.expected_amount:
                order.expected_amount = order.amount_total

    @api.depends(
        'partner_id', 'amount_total', 'state',
        'expected_delivery_date', 'actual_delivery_date',
    )
    def _compute_supplier_score(self):
        """
        Supplier score (0–100):
          Partner set:           +20
          Order confirmed:       +20
          Delivery on time:      +40 | late: +10 | no date: +0
          Amount > 1000:         +10
          Amount > 10000:        +10
        """
        from datetime import date
        today = date.today()
        for order in self:
            score = 0
            if order.partner_id:
                score += 20
            if order.state in ('purchase', 'received', 'invoiced'):
                score += 20
            # Delivery timing
            if order.expected_delivery_date and order.actual_delivery_date:
                delay = (order.actual_delivery_date - order.expected_delivery_date).days
                score += 40 if delay <= 0 else 10
            elif order.expected_delivery_date:
                score += 0  # awaiting delivery
            # Amount bonus
            if (order.amount_total or 0) > 1000:
                score += 10
            if (order.amount_total or 0) > 10000:
                score += 10
            order.supplier_score = min(100.0, float(score))

    @api.depends('expected_delivery_date', 'actual_delivery_date', 'state', 'supplier_score')
    def _compute_delay_risk(self):
        from datetime import date
        today = date.today()
        for order in self:
            pts = 0
            if order.state not in ('received', 'invoiced', 'cancel'):
                if order.expected_delivery_date:
                    delta = (order.expected_delivery_date - today).days
                    if delta < 0:
                        pts += 3  # already late
                    elif delta < 3:
                        pts += 2  # imminent
                else:
                    pts += 1  # no date set
            if (order.supplier_score or 0) < 40:
                pts += 2
            if pts >= 4:
                order.delay_risk = 'high'
            elif pts >= 2:
                order.delay_risk = 'medium'
            else:
                order.delay_risk = 'low'

    @api.depends('state')
    def _compute_invoice_status(self):
        for order in self:
            if order.state in ('purchase', 'received'):
                order.invoice_status = 'to_invoice'
            elif order.state == 'invoiced':
                order.invoice_status = 'invoiced'
            else:
                order.invoice_status = 'no'

    # -- CRUD

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('flowmerce.purchase.order') or _('New')
                )
        return super().create(vals_list)

    # -- Workflow Actions

    def action_rfq_send(self):
        """Mark RFQ as sent."""
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'sent'})
        return True

    def action_confirm(self):
        """Confirm the purchase order."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('Only RFQs can be confirmed.'))
            if not order.order_line:
                raise UserError(_('A purchase order must have at least one line before confirmation.'))
            order.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
            order.message_post(
                body=_('Purchase order confirmed by %s') % self.env.user.name,
                subject=_('Order Confirmed'),
            )
        return True

    def action_received(self):
        """Mark order as received."""
        for order in self:
            if order.state != 'purchase':
                raise UserError(_('Only confirmed orders can be marked as received.'))
            order.write({'state': 'received'})
            order.message_post(body=_('Order received.'), subject=_('Reception Done'))
        return True

    def action_cancel(self):
        """Cancel the order."""
        for order in self:
            if order.state == 'invoiced':
                raise UserError(_('Cannot cancel an invoiced order.'))
            order.write({'state': 'cancel'})
            order.message_post(
                body=_('Order cancelled by %s') % self.env.user.name,
                subject=_('Order Cancelled'),
            )
        return True

    def action_draft(self):
        """Reset to draft."""
        self.filtered(lambda o: o.state == 'cancel').write({'state': 'draft'})
        return True

    def evaluate_supplier(self):
        """Recompute supplier score and delay risk, post result in chatter."""
        self._compute_supplier_score()
        self._compute_delay_risk()
        for order in self:
            order.message_post(
                body=_(
                    'Supplier evaluation updated — Score: %.1f | Delivery Risk: %s'
                ) % (order.supplier_score, order.delay_risk),
                subject=_('Supplier Evaluation — Flowmerce ERP'),
            )
        return True

    @api.model
    def auto_create_purchase_if_needed(self):
        """Called by cron: auto-confirm purchase orders flagged for auto-order."""
        orders = self.search([
            ('auto_order_flag', '=', True),
            ('state', 'in', ('draft', 'sent')),
        ])
        confirmed = 0
        for order in orders:
            if order.order_line:
                order.action_confirm()
                confirmed += 1
        _logger.info('Flowmerce Purchase: %d orders auto-confirmed.', confirmed)
        return True
