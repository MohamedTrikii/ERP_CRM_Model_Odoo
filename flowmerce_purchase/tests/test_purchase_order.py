from datetime import date, timedelta

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFlowmercePurchaseOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({'name': 'Supplier'})
        cls.product = cls.env['product.product'].create({'name': 'Cement', 'standard_price': 10})
        cls.Order = cls.env['flowmerce.purchase.order']

    def _order(self, **vals):
        return self.Order.create({
            'partner_id': self.supplier.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id, 'name': 'Cement', 'product_uom_qty': 5,
                'price_unit': 10, 'product_uom': self.product.uom_id.id,
            })],
            **vals,
        })

    def test_late_unconfirmed_order_is_high_risk(self):
        order = self._order(expected_delivery_date=date.today() - timedelta(days=2))
        self.assertEqual(order.delay_risk, 'high')

    def test_on_time_delivery_raises_supplier_score(self):
        late = self._order(expected_delivery_date=date.today() - timedelta(days=5),
                           actual_delivery_date=date.today())
        on_time = self._order(expected_delivery_date=date.today(), actual_delivery_date=date.today())
        self.assertGreater(on_time.supplier_score, late.supplier_score)

    def test_cron_confirms_only_flagged_orders(self):
        flagged = self._order(auto_order_flag=True)
        manual = self._order()
        self.Order.auto_create_purchase_if_needed()
        self.assertEqual(flagged.state, 'purchase')
        self.assertEqual(manual.state, 'draft')
