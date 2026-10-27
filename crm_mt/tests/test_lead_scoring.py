import math

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestLeadScoring(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'ACME'})
        cls.stage = cls.env['crm.mt.stage'].create({'name': 'Qualified'})
        cls.Lead = cls.env['crm.mt.lead']

    def _recency_points(self, lead):
        d = lead.days_since_activity or 999
        return 20 if d < 7 else 10 if d < 30 else 5 if d < 60 else 0

    def test_score_follows_documented_rule(self):
        lead = self.Lead.create({
            'name': 'Big deal', 'priority': '2', 'expected_revenue': 10000,
            'probability': 50, 'partner_id': self.partner.id, 'stage_id': self.stage.id,
        })
        expected = 25 + min(25, int(math.log10(10001) * 5)) + self._recency_points(lead) + 10 + 10 + 10
        self.assertEqual(lead.lead_score, min(100, expected))

    def test_empty_lead_scores_low_and_score_is_capped(self):
        empty = self.Lead.create({'name': 'Cold contact'})
        self.assertEqual(empty.lead_score, 5 + self._recency_points(empty))
        rich = self.Lead.create({
            'name': 'Huge', 'priority': '2', 'expected_revenue': 10 ** 9, 'probability': 100,
            'partner_id': self.partner.id, 'stage_id': self.stage.id,
        })
        self.assertLessEqual(rich.lead_score, 100)

    def test_high_revenue_lead_is_vip(self):
        lead = self.Lead.create({'name': 'Key account', 'expected_revenue': 60000})
        self.assertEqual(lead.segment_client, 'vip')

    def test_mark_won_and_lost(self):
        lead = self.Lead.create({'name': 'Deal'})
        lead.action_mark_won()
        self.assertEqual((lead.won_status, lead.probability), ('won', 100.0))
        lead.action_mark_lost()
        self.assertEqual((lead.won_status, lead.probability), ('lost', 0.0))
