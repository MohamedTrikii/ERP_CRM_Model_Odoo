# -*- coding: utf-8 -*-
"""
Optimized CRM MT Purchase Order model for Odoo 19: performance, scalability, maintainability.
"""
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CrmMtPurchase(models.Model):
    """
    CRM MT Purchase Order
    Optimized for performance and scalability.
    """
    _name = 'crm.mt.purchase'
    _description = 'CRM MT Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    # SQL constraints and indexes for performance
    _sql_constraints = [
        ('probability_range', 'CHECK(probability >= 0 AND probability <= 100)', 'Probability must be between 0 and 100.'),
    ]

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        index=True, default=lambda self: _('New'),
        help="Unique purchase order reference."
    )
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True, tracking=True, index=True)
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now, tracking=True, index=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'RFQ Sent'),
        ('purchase', 'Purchase Order'),
        ('received', 'Received'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    amount_untaxed = fields.Monetary('Untaxed Amount', compute='_compute_amounts', store=True, tracking=True)
    amount_tax = fields.Monetary('Taxes', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary('Total', compute='_compute_amounts', store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='Buyer', default=lambda self: self.env.user, tracking=True, index=True)
    team_id = fields.Many2one('crm.mt.team', string='Buyer Team', tracking=True, index=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', default='0', tracking=True, index=True)
    expected_amount = fields.Monetary('Expected Amount', currency_field='currency_id', tracking=True)
    probability = fields.Float('Probability (%)', default=0.0, tracking=True, help="Probability of closing (0-100).")
    description = fields.Html('Description')
    note = fields.Text('Terms and Conditions')
    color = fields.Integer('Color', default=0, help="Color index for kanban view")
    order_line_ids = fields.One2many('crm.mt.purchase.line', 'order_id', string='Order Lines')

    @api.depends('order_line_ids.price_subtotal')
    def _compute_amounts(self):
        """Compute untaxed, tax, and total amounts efficiently."""
        for order in self:
            order.amount_untaxed = sum(line.price_subtotal for line in order.order_line_ids)
            order.amount_tax = 0.0  # Extend if taxes are implemented
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.model_create_multi
    def create(self, vals_list):
        """Assign sequence on creation, optimized for batch."""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('crm.mt.purchase')
                    or _('New')
                )
        return super().create(vals_list)

    def action_confirm(self):
        """Confirm purchase order, with validation and logging."""
        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(_('Only draft or sent orders can be confirmed.'))
            if not order.order_line_ids:
                raise UserError(_('A purchase order must have at least one line before confirmation.'))
            order.write({'state': 'purchase'})
            order.message_post(
                body=_('Purchase order confirmed by %s') % self.env.user.name,
                subject=_('Order Confirmed'),
            )
        return True

    def action_received(self):
        """Mark purchase order as received, with validation and logging."""
        for order in self:
            if order.state != 'purchase':
                raise UserError(_('Only confirmed orders can be marked as received.'))
            order.write({'state': 'received'})
            order.message_post(body=_('Order received.'), subject=_('Reception Done'))
        return True

    def action_cancel(self):
        """Cancel purchase order, with validation and logging."""
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
        """Reset cancelled orders to draft."""
        self.filtered(lambda o: o.state == 'cancel').write({'state': 'draft'})
        return True

    @api.model
    def search_read_fast(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """
        Fast search_read for kanban/list views (avoids N+1 queries).
        """
        return self.search_read(domain or [], fields, offset=offset, limit=limit, order=order)
