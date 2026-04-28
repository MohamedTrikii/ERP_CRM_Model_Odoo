# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Statistiques de vente
    sale_order_count = fields.Integer(
        string='Nombre de commandes',
        compute='_compute_sale_order_count'
    )
    
    total_sales = fields.Monetary(
        string='Total des ventes',
        compute='_compute_total_sales',
        currency_field='currency_id'
    )
    
    last_sale_date = fields.Date(
        string='Dernière vente',
        compute='_compute_last_sale_date'
    )

    @api.depends('name')
    def _compute_sale_order_count(self):
        for partner in self:
            partner.sale_order_count = self.env['erp.sale.order'].search_count([
                ('partner_id', 'child_of', partner.id),
                ('state', 'in', ['sale', 'delivered', 'invoiced'])
            ])

    @api.depends('name')
    def _compute_total_sales(self):
        for partner in self:
            orders = self.env['erp.sale.order'].search([
                ('partner_id', 'child_of', partner.id),
                ('state', 'in', ['sale', 'delivered', 'invoiced'])
            ])
            partner.total_sales = sum(orders.mapped('amount_total'))

    @api.depends('name')
    def _compute_last_sale_date(self):
        for partner in self:
            last_order = self.env['erp.sale.order'].search([
                ('partner_id', 'child_of', partner.id),
                ('state', 'in', ['sale', 'delivered', 'invoiced'])
            ], order='date_order desc', limit=1)
            partner.last_sale_date = last_order.date_order.date() if last_order else False

    def action_view_sales(self):
        """Voir les commandes de vente du client"""
        self.ensure_one()
        return {
            'name': 'Commandes de vente',
            'type': 'ir.actions.act_window',
            'res_model': 'erp.sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', 'child_of', self.id)],
            'context': {'default_partner_id': self.id}
        }