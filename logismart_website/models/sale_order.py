# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    saas_license_count = fields.Integer(string="Nombre de Licences SaaS", compute='_compute_saas_license_count')

    @api.depends('order_line')
    def _compute_saas_license_count(self):
        for order in self:
            order.saas_license_count = self.env['logismart.saas.license'].search_count([('sale_order_id', '=', order.id)])

    def action_view_saas_licenses(self):
        self.ensure_one()
        return {
            'name': 'Licences SaaS',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'logismart.saas.license',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id, 'default_partner_id': self.partner_id.id},
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            has_saas = False
            for line in order.order_line:
                if line.product_template_id.is_saas_software:
                    has_saas = True
                    # 1. Génération de la licence
                    self.env['logismart.saas.license'].create({
                        'partner_id': order.partner_id.id,
                        'product_id': line.product_id.id,
                        'sale_line_id': line.id,
                        'sale_order_id': order.id,
                    })
            
            # 2. Génération automatique d'un Lead CRM MT
            if has_saas:
                self.env['crm.mt.lead'].sudo().create({
                    'name': f"Onboarding SaaS - {order.partner_id.name}",
                    'expected_revenue': order.amount_total,
                    'priority': '1',
                    'description': "Nouveau client SaaS suite à la commande " + order.name,
                    'sale_order_id': order.id,
                })
        return res
