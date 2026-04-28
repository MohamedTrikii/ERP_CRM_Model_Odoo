# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Commande de Vente'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, date_order desc, id desc'

    # Informations de base
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('Nouveau')
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain="[('customer_rank', '>', 0)]"
    )
    
    partner_invoice_id = fields.Many2one(
        'res.partner',
        string='Adresse de facturation',
        compute='_compute_partner_invoice_id',
        store=True,
        readonly=False
    )
    
    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Adresse de livraison',
        compute='_compute_partner_shipping_id',
        store=True,
        readonly=False
    )
    
    # Dates
    date_order = fields.Datetime(
        string='Date de commande',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    
    validity_date = fields.Date(
        string="Date d'expiration",
        compute='_compute_validity_date',
        store=True,
        readonly=False
    )
    
    commitment_date = fields.Datetime(
        string='Date de livraison prévue',
        tracking=True
    )
    
    # Statut et workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Devis envoyé'),
        ('sale', 'Commande confirmée'),
        ('delivered', 'Livré'),
        ('invoiced', 'Facturé'),
        ('cancel', 'Annulé'),
    ], string='Statut', readonly=True, copy=False, index=True,
       tracking=True, default='draft')
    
    # Lignes de commande
    order_line = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Lignes de commande',
        copy=True,
        auto_join=True
    )
    
    # Montants
    amount_untaxed = fields.Monetary(
        string='Montant HT',
        store=True,
        compute='_compute_amounts',
        tracking=True
    )
    
    amount_tax = fields.Monetary(
        string='Taxes',
        store=True,
        compute='_compute_amounts'
    )
    
    amount_total = fields.Monetary(
        string='Total TTC',
        store=True,
        compute='_compute_amounts',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    # Utilisateur et équipe
    user_id = fields.Many2one(
        'res.users',
        string='Commercial',
        default=lambda self: self.env.user,
        tracking=True
    )
    
    team_id = fields.Many2one(
        'crm.team',
        string='Équipe de vente',
        tracking=True
    )
    
    # Notes
    note = fields.Text(string='Conditions générales')
    client_order_ref = fields.Char(string='Référence client')
    
    # Facturation
    invoice_count = fields.Integer(
        string='Nombre de factures',
        compute='_compute_invoice_count'
    )
    
    invoice_ids = fields.Many2many(
        'account.move',
        string='Factures',
        copy=False
    )
    
    invoice_status = fields.Selection([
        ('no', 'Rien à facturer'),
        ('to_invoice', 'À facturer'),
        ('invoiced', 'Totalement facturé'),
    ], string='Statut facturation', compute='_compute_invoice_status',
       store=True, readonly=True, default='no')

    # Champs analytiques et enrichissements CRM
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priorité', index=True, default='0', tracking=True)

    expected_revenue = fields.Monetary('Revenu attendu', currency_field='currency_id', tracking=True, default=0.0)
    probability = fields.Float('Probabilité de succès (%)', default=0.0, tracking=True)
    description = fields.Html('Description')
    partner_email = fields.Char(related='partner_id.email', string='Email Client', readonly=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Téléphone Client', readonly=True)

    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'utm.mixin',
        'format.address.mixin',
        'mail.tracking.duration.mixin',
    ]
    _order = 'priority desc, date_order desc, id desc'

    # Champs calculés
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
                order.validity_date = order.date_order + timedelta(days=30)
            else:
                order.validity_date = False

    @api.depends('order_line.price_subtotal')
    def _compute_amounts(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = 0.0  # À compléter selon la gestion de la TVA
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax
            # Calcul du revenu attendu si non saisi
            if not order.expected_revenue:
                order.expected_revenue = order.amount_total

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    @api.depends('state', 'order_line.invoice_status')
    def _compute_invoice_status(self):
        for order in self:
            if order.state not in ('sale', 'delivered', 'invoiced'):
                order.invoice_status = 'no'
            elif order.state == 'invoiced':
                order.invoice_status = 'invoiced'
            elif any(line.invoice_status == 'to_invoice' for line in order.order_line):
                order.invoice_status = 'to_invoice'
            else:
                order.invoice_status = 'invoiced' if order.invoice_ids else 'no'

    # Méthodes CRUD
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('Nouveau')
            # Calcul automatique de la probabilité si non fournie
            if 'probability' not in vals or vals['probability'] is None:
                vals['probability'] = 100.0 if vals.get('state') == 'sale' else 0.0
        return super(SaleOrder, self).create(vals_list)

    # Actions de workflow
    def action_quotation_send(self):
        """Marquer le devis comme envoyé"""
        self.ensure_one()
        if self.state == 'draft':
            self.state = 'sent'
        return True

    def action_confirm(self):
        """Confirmer la commande"""
        for order in self:
            if order.state not in ['draft', 'sent']:
                raise UserError(_('Seuls les devis peuvent être confirmés.'))
            order.state = 'sale'
            # Message dans le chatter
            order.message_post(
                body=_('Commande confirmée par %s') % self.env.user.name,
                subject=_('Commande confirmée')
            )
        return True

    def action_delivered(self):
        """Marquer comme livré"""
        for order in self:
            if order.state != 'sale':
                raise UserError(_('Seules les commandes confirmées peuvent être marquées comme livrées.'))
            order.state = 'delivered'
            order.message_post(
                body=_('Commande livrée'),
                subject=_('Livraison effectuée')
            )
        return True

    def action_cancel(self):
        """Annuler la commande"""
        for order in self:
            if order.state == 'invoiced':
                raise UserError(_('Impossible d\'annuler une commande facturée.'))
            order.state = 'cancel'
            order.message_post(
                body=_('Commande annulée par %s') % self.env.user.name,
                subject=_('Commande annulée')
            )
        return True

    def action_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft'})
        return True

    def action_create_invoice(self):
        self.ensure_one()
        return {
            'name': _('Créer une facture'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_order_id': self.id}
        }

    def action_view_invoices(self):
        """Voir les factures liées"""
        self.ensure_one()
        return {
            'name': _('Factures'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }

    # Contraintes
    @api.constrains('order_line')
    def _check_order_line(self):
        for order in self:
            if not order.order_line:
                raise ValidationError(_('Une commande doit avoir au moins une ligne.'))
    @api.constrains('order_line', 'probability')
    def _check_order_line_probability(self):
        for order in self:
            if not order.order_line:
                raise ValidationError(_('Une commande doit avoir au moins une ligne.'))
            if order.state == 'sale' and order.probability < 100:
                raise ValidationError(_('Une commande confirmée doit avoir une probabilité de 100%.'))