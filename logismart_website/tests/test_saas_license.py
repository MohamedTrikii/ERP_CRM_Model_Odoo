from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSaasLicense(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'SaaS customer', 'email': 'customer@example.com'})
        cls.saas = cls.env['product.product'].create({
            'name': 'ERP Cloud', 'list_price': 300, 'is_saas_software': True, 'license_duration_days': 30,
        })
        cls.lifetime = cls.env['product.product'].create({
            'name': 'Desktop tool', 'is_saas_software': True, 'license_duration_days': 0,
        })

    def test_confirming_order_creates_licence_and_onboarding_lead(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {'product_id': self.saas.id, 'product_uom_qty': 1})],
        })
        order.action_confirm()
        licence = self.env['logismart.saas.license'].search([('sale_order_id', '=', order.id)])
        self.assertEqual(len(licence), 1)
        self.assertEqual(licence.state, 'active')
        self.assertEqual((licence.expiration_date - licence.activation_date).days, 30)
        lead = self.env['crm.mt.lead'].search([('sale_order_id', '=', order.id)])
        self.assertEqual(len(lead), 1)

    def test_lifetime_licence_never_expires(self):
        licence = self.env['logismart.saas.license'].create({'partner_id': self.partner.id, 'product_id': self.lifetime.id})
        self.assertFalse(licence.expiration_date)

    def test_expired_licences_are_closed(self):
        licence = self.env['logismart.saas.license'].create({
            'partner_id': self.partner.id, 'product_id': self.saas.id,
            'expiration_date': fields.Datetime.now() - timedelta(days=1),
        })
        licence.check_expirations()
        self.assertEqual(licence.state, 'expired')
