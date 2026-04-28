from odoo import models, fields

class CrmMtLostReason(models.Model):
    _name = 'crm.mt.lost.reason'
    _description = 'CRM_MT Lost Reason'

    name = fields.Char('Reason', required=True)
    active = fields.Boolean('Active', default=True)
