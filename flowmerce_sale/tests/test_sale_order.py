from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFlowmerceSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Client'})
        cls.product = cls.env['product.product'].create({'name': 'Widget', 'list_price': 100, 'standard_price': 60})
        cls.Order = cls.env['flowmerce.sale.order']

    def _order(self, **vals):
        return self.Order.create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id, 'name': 'Widget', 'product_uom_qty': 2,
                'price_unit': 100, 'cost_price': 60, 'product_uom': self.product.uom_id.id,
            })],
            **vals,
        })

    def test_sequence_and_margin(self):
        order = self._order()
        self.assertTrue(order.name.startswith('SO'))
        self.assertAlmostEqual(order.margin, 80.0)          # 2 × (100 − 60)
        self.assertAlmostEqual(order.margin_rate, 40.0)     # 80 / 200

    def test_confirm_requires_lines(self):
        empty = self.Order.create({'partner_id': self.partner.id})
        with self.assertRaises(UserError):
            empty.action_confirm()
        order = self._order()
        order.action_confirm()
        self.assertEqual(order.state, 'sale')

    def test_stale_quotation_follow_up(self):
        stale = self._order(date_order=fields.Datetime.now() - timedelta(days=10))
        fresh = self._order()
        before_stale, before_fresh = len(stale.message_ids), len(fresh.message_ids)
        self.Order.cron_auto_followup_quotations()
        self.assertGreater(len(stale.message_ids), before_stale)
        self.assertEqual(len(fresh.message_ids), before_fresh)
