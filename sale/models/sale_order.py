# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    # -- Identification
    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'),
    )

    # -- Partners
    partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True, index=True,
    )
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        compute='_compute_partner_invoice_id', store=True, readonly=False,
    )
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address',
        compute='_compute_partner_shipping_id', store=True, readonly=False,
    )

    # -- Dates
    date_order = fields.Datetime(
        string='Order Date', required=True, default=fields.Datetime.now, tracking=True,
    )
    validity_date = fields.Date(
        string='Expiration Date', compute='_compute_validity_date', store=True, readonly=False,
    )
    commitment_date = fields.Datetime(string='Delivery Date', tracking=True)

    # -- Status
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('delivered', 'Delivered'),
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
        'sale.order.line', 'order_id', string='Order Lines', copy=True, auto_join=True,
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

    # -- Sales Info
    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user, tracking=True,
    )
    team_id = fields.Many2one('crm.mt.team', string='Sales Team', tracking=True)
    client_order_ref = fields.Char(string='Customer Reference')
    note = fields.Text(string='Terms and Conditions')

    # -- Analytics
    priority = fields.Selection([
        ('0', 'Normal'), ('1', 'Important'), ('2', 'Urgent'),
    ], string='Priority', index=True, default='0', tracking=True)
    expected_revenue = fields.Monetary(
        string='Expected Revenue', currency_field='currency_id', tracking=True, default=0.0,
    )
    probability = fields.Float(string='Success Probability (%)', default=0.0, tracking=True)
    description = fields.Html(string='Description')
    partner_email = fields.Char(related='partner_id.email', string='Customer Email', readonly=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Customer Phone', readonly=True)

    # -- Flowmerce: Margin & Profitability
    margin = fields.Monetary(
        string='Margin', compute='_compute_margin', store=True,
        currency_field='currency_id', tracking=True,
    )
    margin_rate = fields.Float(
        string='Margin (%)', compute='_compute_margin', store=True,
        digits=(16, 2), tracking=True,
    )
    discount_global = fields.Float(
        string='Global Discount (%)', default=0.0, digits=(16, 2), tracking=True,
        help="Additional global discount applied on top of line discounts.",
    )

    # -- Flowmerce: Payment Status
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='unpaid', tracking=True, index=True)

    # -- Computed Methods

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            if order.partner_id:
                order.partner_invoice_id = order.partner_id.address_get(['invoice'])['invoice']
            else:
                order.partner_invoice_id = False

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            if order.partner_id:
                order.partner_shipping_id = order.partner_id.address_get(['delivery'])['delivery']
            else:
                order.partner_shipping_id = False

    @api.depends('date_order')
    def _compute_validity_date(self):
        for order in self:
            if order.date_order:
                order.validity_date = order.date_order.date() + timedelta(days=30)
            else:
                order.validity_date = False

    @api.depends('order_line.price_subtotal', 'discount_global')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            if order.discount_global:
                amount_untaxed = amount_untaxed * (1.0 - order.discount_global / 100.0)
            order.amount_untaxed = amount_untaxed
            order.amount_tax = 0.0
            order.amount_total = amount_untaxed
            if not order.expected_revenue:
                order.expected_revenue = order.amount_total

    @api.depends('order_line.margin', 'amount_untaxed')
    def _compute_margin(self):
        for order in self:
            order.margin = sum(line.margin for line in order.order_line)
            if order.amount_untaxed:
                order.margin_rate = (order.margin / order.amount_untaxed) * 100.0
            else:
                order.margin_rate = 0.0

    @api.depends('state')
    def _compute_invoice_status(self):
        for order in self:
            if order.state in ('sale', 'delivered'):
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
                    self.env['ir.sequence'].next_by_code('sale.order') or _('New')
                )
        return super().create(vals_list)

    # -- Workflow Actions

    def action_quotation_send(self):
        """Mark quotation as sent."""
        self.ensure_one()
        if self.state == 'draft':
            self.write({'state': 'sent'})
        return True

    def action_confirm(self):
        """Confirm the sale order."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('Only quotations can be confirmed.'))
            if not order.order_line:
                raise UserError(_('A sale order must have at least one line before confirmation.'))
            order.write({'state': 'sale'})
            order.message_post(
                body=_('Order confirmed by %s') % self.env.user.name,
                subject=_('Order Confirmed'),
            )
        return True

    def action_delivered(self):
        """Mark order as delivered."""
        for order in self:
            if order.state != 'sale':
                raise UserError(_('Only confirmed orders can be marked as delivered.'))
            order.write({'state': 'delivered'})
            order.message_post(body=_('Order delivered.'), subject=_('Delivery Done'))
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

    def action_create_invoice(self):
        """Open the invoice creation wizard."""
        self.ensure_one()
        return {
            'name': _('Create Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def action_confirm_auto(self):
        """Auto-confirm all draft/sent orders in the recordset."""
        for order in self.filtered(lambda o: o.state in ('draft', 'sent')):
            order.action_confirm()
        return True

    def generate_invoice_auto(self):
        """Auto-generate invoice wizard for confirmed/delivered orders."""
        for order in self.filtered(lambda o: o.state in ('sale', 'delivered')):
            order.action_create_invoice()
        return True

    def action_mark_paid(self):
        """Mark payment status as paid."""
        self.write({'payment_status': 'paid', 'state': 'invoiced'})
        for order in self:
            order.message_post(
                body=_('Payment received — order marked as Paid.'),
                subject=_('Payment Confirmed'),
            )
        return True

    def action_mark_partial(self):
        """Mark payment status as partially paid."""
        self.write({'payment_status': 'partial'})
        return True

    @api.model
    def cron_auto_followup_quotations(self):
        """Cron: auto-send a follow-up message on quotations not confirmed after 7 days."""
        from datetime import timedelta
        cutoff = fields.Datetime.now() - timedelta(days=7)
        stale = self.search([
            ('state', 'in', ('draft', 'sent')),
            ('date_order', '<=', cutoff),
        ])
        for order in stale:
            order.message_post(
                body=_('⚠️ Flowmerce ERP: this quotation has been pending for over 7 days. Please follow up with the customer.'),
                subject=_('Quotation Follow-up Reminder'),
            )
        _logger.info('Flowmerce Sale: %d stale quotations flagged for follow-up.', len(stale))
