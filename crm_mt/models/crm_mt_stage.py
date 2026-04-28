from odoo import models, fields

class CrmMtStage(models.Model):
    _name = 'crm.mt.stage'
    _description = 'CRM_MT Stage'
    _order = 'sequence, name, id'

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1)
    is_won = fields.Boolean('Is Won Stage?')
    fold = fields.Boolean('Folded in Pipeline')
    color = fields.Integer('Color')
    team_ids = fields.Many2many('crm.mt.team', string='Teams')
    requirements = fields.Text('Requirements')
