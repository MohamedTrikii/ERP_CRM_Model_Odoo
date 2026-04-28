from odoo import models, fields

class CrmMtTeam(models.Model):
    _name = 'crm.mt.team'
    _description = 'CRM_MT Team'

    name = fields.Char('Team Name', required=True)
    user_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.Many2many('res.users', string='Team Members')
