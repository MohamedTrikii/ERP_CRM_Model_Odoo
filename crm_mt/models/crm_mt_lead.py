# -*- coding: utf-8 -*-
"""
LogiSmart ERP — Enhanced CRM Lead model (Odoo 19).
AI-powered scoring, risk detection, automatic segmentation.
"""
import math
import logging
from datetime import date, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CrmMtLead(models.Model):
    """
    Lead/Opportunity — LogiSmart ERP
    Includes AI scoring, segmentation, risk detection.
    """
    _name = 'crm.mt.lead'
    _description = 'Lead/Opportunity (LogiSmart ERP)'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'priority desc, lead_score desc, id desc'

    _probability_range = models.Constraint(
        'CHECK(probability >= 0 AND probability <= 100)',
        'Probability must be between 0 and 100.',
    )

    # ── Core Fields ───────────────────────────────────────────────────────────
    name = fields.Char('Title', required=True, tracking=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Contact', tracking=True, index=True)
    user_id = fields.Many2one('res.users', string='Assigned to', tracking=True, index=True)
    team_id = fields.Many2one('crm.mt.team', string='Team', tracking=True, index=True)
    stage_id = fields.Many2one('crm.mt.stage', string='Stage', tracking=True, index=True)
    expected_revenue = fields.Monetary(
        'Expected Revenue', currency_field='currency_id', tracking=True,
    )
    probability = fields.Float(
        'Probability (%)', default=0.0, tracking=True,
        help="Win probability (0–100). Auto-computed from score if left at 0.",
    )
    priority = fields.Selection([
        ('0', 'Normal'), ('1', 'Important'), ('2', 'Urgent'),
    ], string='Priority', default='0', tracking=True, index=True)
    description = fields.Html('Description')
    date_deadline = fields.Date('Expected Closing', index=True)
    lost_reason_id = fields.Many2one('crm.mt.lost.reason', string='Lost Reason', index=True)
    active = fields.Boolean('Active', default=True, index=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    won_status = fields.Selection([
        ('won', 'Won'), ('lost', 'Lost'), ('pending', 'Pending'),
    ], string='Status', default='pending', tracking=True, index=True)

    # ── AI / Intelligence Fields ──────────────────────────────────────────────
    lead_score = fields.Integer(
        string='Lead Score', compute='_compute_lead_score', store=True,
        help="CRM_TRIKI AI score (0–100) based on activity, revenue, priority and history.",
    )
    segment_client = fields.Selection([
        ('vip', 'VIP'),
        ('loyal', 'Loyal'),
        ('at_risk', 'At Risk'),
        ('new', 'New'),
        ('cold', 'Cold'),
    ], string='Client Segment', compute='_compute_segment', store=True, tracking=True)
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], string='Risk Level', compute='_compute_risk_level', store=True, tracking=True)
    last_activity_date = fields.Date(
        string='Last Activity Date',
        compute='_compute_last_activity_date', store=True,
    )
    days_since_activity = fields.Integer(
        string='Days Since Activity',
        compute='_compute_last_activity_date', store=True,
    )

    # ── Constraints ───────────────────────────────────────────────────────────
    @api.constrains('probability')
    def _check_probability(self):
        for rec in self:
            if rec.probability < 0 or rec.probability > 100:
                raise ValidationError('Probability must be between 0 and 100.')

    # ── Computed: Last Activity ───────────────────────────────────────────────
    @api.depends('activity_ids', 'activity_ids.date_deadline')
    def _compute_last_activity_date(self):
        today = date.today()
        for lead in self:
            activities = lead.activity_ids.filtered(lambda a: a.date_deadline)
            if activities:
                last = max(activities.mapped('date_deadline'))
                lead.last_activity_date = last
                lead.days_since_activity = (today - last).days
            else:
                lead.last_activity_date = False
                lead.days_since_activity = 999

    # ── Computed: Lead Score (CRM_TRIKI AI Logic) ─────────────────────────────
    @api.depends(
        'priority', 'expected_revenue', 'probability',
        'days_since_activity', 'partner_id', 'stage_id',
    )
    def _compute_lead_score(self):
        """
        Scoring rule (0–100):
          Priority:          0→5 | 1→15 | 2→25
          Expected revenue:  up to 25 pts (log scale)
          Activity recency:  <7d→20 | <30d→10 | <60d→5 | ≥60d→0
          Partner set:       +10
          Stage set:         +10
          Probability:       /5 (max 20 pts)
        """
        for lead in self:
            score = {'0': 5, '1': 15, '2': 25}.get(lead.priority or '0', 5)
            if lead.expected_revenue and lead.expected_revenue > 0:
                score += min(25, int(math.log10(lead.expected_revenue + 1) * 5))
            d = lead.days_since_activity or 999
            if d < 7:
                score += 20
            elif d < 30:
                score += 10
            elif d < 60:
                score += 5
            if lead.partner_id:
                score += 10
            if lead.stage_id:
                score += 10
            score += int((lead.probability or 0) / 5)
            lead.lead_score = min(100, score)

    # ── Computed: Client Segment ──────────────────────────────────────────────
    @api.depends('lead_score', 'expected_revenue', 'won_status', 'days_since_activity')
    def _compute_segment(self):
        for lead in self:
            score = lead.lead_score or 0
            days = lead.days_since_activity or 999
            rev = lead.expected_revenue or 0
            if score >= 75 or rev >= 50000:
                lead.segment_client = 'vip'
            elif score >= 55 and days < 30:
                lead.segment_client = 'loyal'
            elif days >= 60 or score < 20:
                lead.segment_client = 'cold'
            elif lead.won_status == 'pending' and days >= 30:
                lead.segment_client = 'at_risk'
            else:
                lead.segment_client = 'new'

    # ── Computed: Risk Level ──────────────────────────────────────────────────
    @api.depends('lead_score', 'days_since_activity', 'date_deadline', 'probability')
    def _compute_risk_level(self):
        today = date.today()
        for lead in self:
            pts = 0
            if (lead.lead_score or 0) < 25:
                pts += 2
            if (lead.days_since_activity or 999) >= 30:
                pts += 2
            if lead.date_deadline and lead.date_deadline < today:
                pts += 3
            if (lead.probability or 0) < 20:
                pts += 1
            if pts >= 5:
                lead.risk_level = 'high'
            elif pts >= 2:
                lead.risk_level = 'medium'
            else:
                lead.risk_level = 'low'

    # ── Public AI Methods ─────────────────────────────────────────────────────
    def compute_score(self):
        """Recompute lead score, segment and risk level."""
        self._compute_lead_score()
        self._compute_segment()
        self._compute_risk_level()
        return True

    def compute_probability(self):
        """Auto-set probability from lead score (only if not manually set)."""
        for lead in self:
            lead._compute_lead_score()
            if not lead.probability:
                lead.probability = min(100.0, float(lead.lead_score))
        return True

    def detect_risk(self):
        """Flag high-risk leads and post a chatter message."""
        self._compute_risk_level()
        for lead in self.filtered(lambda l: l.risk_level == 'high'):
            lead.message_post(
                body="⚠️ CRM_TRIKI AI: this lead is flagged as HIGH RISK. Immediate follow-up required.",
                subject="Risk Alert — CRM_TRIKI ERP",
            )
        return True

    def action_recompute_ai(self):
        """Button action: trigger all AI computations and display notification."""
        self.compute_score()
        self.compute_probability()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'CRM_TRIKI AI',
                'message': 'Score, segment and risk recomputed successfully.',
                'sticky': False,
                'type': 'success',
            },
        }

    # ── Workflow Actions ──────────────────────────────────────────────────────
    def action_mark_won(self):
        self.write({'won_status': 'won', 'probability': 100.0})

    def action_mark_lost(self):
        self.write({'won_status': 'lost', 'probability': 0.0})

    def action_create_quotation(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Quotation',
            'res_model': 'crm.mt.sale',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_lead_id': self.id,
            },
        }

    # ── Cron: Inactive Lead Check ─────────────────────────────────────────────
    @api.model
    def cron_check_inactive_leads(self):
        """Cron job: notify on leads inactive for 30+ days."""
        leads = self.search([('won_status', '=', 'pending'), ('active', '=', True)])
        flagged = 0
        for lead in leads:
            if (lead.days_since_activity or 999) >= 30:
                lead.message_post(
                    body=f"⚠️ No activity for {lead.days_since_activity} days. Please follow up.",
                    subject="Inactivity Alert — CRM_TRIKI ERP",
                )
                flagged += 1
        _logger.info("CRM_TRIKI CRM: %d leads flagged for inactivity.", flagged)
