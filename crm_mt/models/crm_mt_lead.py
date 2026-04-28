from odoo import models, fields, api

class CrmMtLead(models.Model):
    _name = 'crm.mt.lead'
    _description = 'Lead/Opportunity (CRM_MT)'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char('Title', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Contact', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True)
    team_id = fields.Many2one('crm.mt.team', string='Team', tracking=True)
    stage_id = fields.Many2one('crm.mt.stage', string='Stage', tracking=True)
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='currency_id', tracking=True)
    probability = fields.Float('Probability (%)', default=0.0, tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
        ('2', 'Urgent'),
    ], string='Priority', default='0', tracking=True)
    description = fields.Html('Description')
    date_deadline = fields.Date('Expected Closing')
    lost_reason_id = fields.Many2one('crm.mt.lost.reason', string='Lost Reason')
    active = fields.Boolean('Active', default=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
    ], string='Status', default='pending', tracking=True)

    @api.constrains('probability')
    def _check_probability(self):
        for rec in self:
            if rec.probability < 0 or rec.probability > 100:
                raise ValidationError('Probability must be between 0 and 100.')
