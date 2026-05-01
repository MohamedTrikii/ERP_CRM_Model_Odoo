# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    saas_license_count = fields.Integer(compute='_compute_saas_license_count')
    crm_mt_lead_count = fields.Integer(compute='_compute_crm_mt_lead_count')

    def _compute_saas_license_count(self):
        for partner in self:
            partner.saas_license_count = self.env['logismart.saas.license'].search_count([('partner_id', '=', partner.id)])

    def _compute_crm_mt_lead_count(self):
        for partner in self:
            partner.crm_mt_lead_count = self.env['crm.mt.lead'].search_count([('partner_id', '=', partner.id)])

    def action_view_saas_licenses(self):
        return {
            'name': 'Licences SaaS',
            'type': 'ir.actions.act_window',
            'res_model': 'logismart.saas.license',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }

    def action_view_crm_leads(self):
        return {
            'name': 'Leads CRM LogiSmart',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.mt.lead',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    saas_license_ids = fields.One2many('logismart.saas.license', 'product_id', string="Licences Vendues")
    license_count = fields.Integer(compute='_compute_license_count')

    def _compute_license_count(self):
        for product in self:
            product.license_count = self.env['logismart.saas.license'].search_count([('product_id.product_tmpl_id', '=', product.id)])

    def action_view_licenses(self):
        return {
            'name': 'Licences Vendues',
            'type': 'ir.actions.act_window',
            'res_model': 'logismart.saas.license',
            'view_mode': 'list,form',
            'domain': [('product_id.product_tmpl_id', '=', self.id)],
        }
