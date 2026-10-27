# -*- coding: utf-8 -*-
from odoo import models, fields, api
import uuid
from datetime import timedelta

class SaasLicense(models.Model):
    _name = 'logismart.saas.license'
    _description = 'Licence Logiciel SaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Clé de Licence", required=True, copy=False, readonly=True, default=lambda self: str(uuid.uuid4()))
    partner_id = fields.Many2one('res.partner', string="Client", required=True)
    product_id = fields.Many2one('product.product', string="Logiciel", required=True)
    sale_line_id = fields.Many2one('sale.order.line', string="Ligne de commande")
    sale_order_id = fields.Many2one('sale.order', string="Commande de Vente", readonly=True)
    state = fields.Selection([
        ('trial', 'Essai Gratuit'),
        ('active', 'Active'),
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée')
    ], string="Statut", default='active', tracking=True)
    activation_date = fields.Datetime("Date d'activation", default=fields.Datetime.now)
    expiration_date = fields.Datetime("Date d'expiration", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Expiration follows the product's licence duration (0 = lifetime licence).
        for vals in vals_list:
            if vals.get('expiration_date') or not vals.get('product_id'):
                continue
            product = self.env['product.product'].browse(vals['product_id'])
            days = product.product_tmpl_id.license_duration_days
            if days > 0:
                start = fields.Datetime.to_datetime(vals.get('activation_date')) or fields.Datetime.now()
                vals['expiration_date'] = start + timedelta(days=days)
        licenses = super(SaasLicense, self).create(vals_list)
        for lic in licenses:
            template = self.env.ref('logismart_website.email_template_saas_license', raise_if_not_found=False)
            if template and lic.partner_id.email:
                template.send_mail(lic.id, force_send=True)
        return licenses

    def check_expirations(self):
        expired_licenses = self.search([('state', 'in', ['active', 'trial']), ('expiration_date', '<', fields.Datetime.now())])
        expired_licenses.write({'state': 'expired'})
