from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    name = fields.Char('Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('invoiced', 'Invoiced'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    amount_untaxed = fields.Monetary('Untaxed Amount', compute='_compute_amounts', store=True, tracking=True)
    amount_tax = fields.Monetary('Taxes', compute='_compute_amounts', store=True)
    amount_total = fields.Monetary('Total', compute='_compute_amounts', store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    user_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user, tracking=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', default='0', tracking=True)
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='currency_id', tracking=True)
    probability = fields.Float('Probability (%)', default=0.0, tracking=True)
    description = fields.Html('Description')
    note = fields.Text('Terms and Conditions')

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amounts(self):
        for order in self:
            order.amount_untaxed = 0.0
            order.amount_tax = 0.0
            order.amount_total = order.amount_untaxed + order.amount_tax
