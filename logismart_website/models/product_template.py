# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_saas_software = fields.Boolean(string="Est un logiciel SaaS", default=False)
    software_version = fields.Char(string="Version logicielle")
    license_duration_days = fields.Integer(string="Durée Licence (jours)", default=30, help="0 pour à vie")
    saas_features = fields.Html(string="Fonctionnalités SaaS")
