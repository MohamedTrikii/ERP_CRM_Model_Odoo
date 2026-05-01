# -*- coding: utf-8 -*-
from odoo import models, fields

class CrmMtLead(models.Model):
    _inherit = 'crm.mt.lead'

    sale_order_id = fields.Many2one('sale.order', string="Commande Vente", readonly=True)
    saas_license_id = fields.Many2one('logismart.saas.license', string="Licence SaaS", readonly=True)
