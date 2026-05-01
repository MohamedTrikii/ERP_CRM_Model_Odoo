# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    saas_health_score = fields.Integer(string="SaaS Health Score", compute='_compute_saas_health_score', store=True)

    @api.depends('sale_order_ids.state')
    def _compute_saas_health_score(self):
        for partner in self:
            licenses = self.env['logismart.saas.license'].search([('partner_id', '=', partner.id)])
            score = 0
            if licenses:
                score += 40 # A déjà acheté du SaaS
                active_licenses = licenses.filtered(lambda l: l.state == 'active')
                if active_licenses:
                    score += 40 # Utilise activement
                if len(licenses) > 1:
                    score += 20 # Client fidèle (upsell)
            partner.saas_health_score = min(score, 100)
