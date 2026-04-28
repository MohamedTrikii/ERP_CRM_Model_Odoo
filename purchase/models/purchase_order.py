from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _description = 'Purchase Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Supplier', required=True, tracking=True)
    date_order = fields.Datetime(string='Order Date', required=True, default=fields.Datetime.now, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'RFQ Sent'),
        ('purchase', 'Purchase Order'),
        ('received', 'Received'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', copy=True, auto_join=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, compute='_compute_amounts', tracking=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string='Total', store=True, compute='_compute_amounts', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='Buyer', default=lambda self: self.env.user, tracking=True)
    note = fields.Text(string='Terms and Conditions')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    invoice_ids = fields.Many2many('account.move', string='Invoices', copy=False)
    invoice_status = fields.Selection([
        ('no', 'Nothing to Invoice'),
        ('to_invoice', 'To Invoice'),
        ('invoiced', 'Fully Invoiced'),
    ], string='Invoice Status', compute='_compute_invoice_status', store=True, readonly=True, default='no')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', index=True, default='0', tracking=True)
    expected_amount = fields.Monetary('Expected Amount', currency_field='currency_id', tracking=True, default=0.0)
    probability = fields.Float('Success Probability (%)', default=0.0, tracking=True)
    description = fields.Html('Description')
    partner_email = fields.Char(related='partner_id.email', string='Supplier Email', readonly=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Supplier Phone', readonly=True)
    team_id = fields.Many2one('crm.team', string='Buyer Team', tracking=True)

    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'utm.mixin',
        'format.address.mixin',
        'mail.tracking.duration.mixin',
    ]

    @api.depends('order_line.price_subtotal')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = 0.0  # To be completed for taxes
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
            # Calcul du montant attendu si non saisi
            if not order.expected_amount:
                order.expected_amount = order.amount_total

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    @api.depends('state', 'order_line')
    def _compute_invoice_status(self):
        for order in self:
            if order.state not in ('purchase', 'received', 'invoiced'):
                order.invoice_status = 'no'
            elif order.state == 'invoiced':
                order.invoice_status = 'invoiced'
            elif any(order.order_line):
                order.invoice_status = 'to_invoice'
            else:
                order.invoice_status = 'invoiced' if order.invoice_ids else 'no'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or _('New')
            # Calcul automatique de la probabilité si non fournie
            if 'probability' not in vals or vals['probability'] is None:
                vals['probability'] = 100.0 if vals.get('state') == 'purchase' else 0.0
        return super(PurchaseOrder, self).create(vals_list)

    @api.constrains('order_line', 'probability')
    def _check_order_line(self):
        for order in self:
            if not order.order_line:
                raise ValidationError(_('A purchase order must have at least one line.'))
            if order.state == 'purchase' and order.probability < 100:
                raise ValidationError(_('A confirmed purchase order must have a probability of 100%.'))

    def action_rfq_send(self):
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'sent'
        return True

    def action_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                raise UserError(_('Only draft or sent RFQs can be confirmed.'))
            order.state = 'purchase'
            order.message_post(body=_('Purchase order confirmed by %s') % self.env.user.name, subject=_('Order Confirmed'))
        return True

    def action_received(self):
        for order in self:
            if order.state != 'purchase':
                raise UserError(_('Only confirmed orders can be marked as received.'))
            order.state = 'received'
            order.message_post(body=_('Order received'), subject=_('Reception done'))
        return True

    def action_cancel(self):
        for order in self:
            if order.state == 'invoiced':
                raise UserError(_('Cannot cancel an invoiced order.'))
            order.state = 'cancel'
            order.message_post(body=_('Order cancelled by %s') % self.env.user.name, subject=_('Order Cancelled'))
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    def action_create_invoice(self):
        self.ensure_one()
        return {
            'name': _('Create Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }

    @api.constrains('order_line')
    def _check_order_line(self):
        for order in self:
            if not order.order_line:
                raise ValidationError(_('A purchase order must have at least one line.'))
