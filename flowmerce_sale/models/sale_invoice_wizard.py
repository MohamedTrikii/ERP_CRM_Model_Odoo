# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleInvoiceWizard(models.TransientModel):
    """Wizard to create an invoice from a sale order."""
    _name = 'flowmerce.sale.invoice.wizard'
    _description = 'Sale Invoice Wizard'

    order_id = fields.Many2one(
        'flowmerce.sale.order', string='Sale Order', required=True, ondelete='cascade',
    )
    invoice_date = fields.Date(
        string='Invoice Date', default=fields.Date.today, required=True,
    )

    def action_create_invoice(self):
        """Create the invoice for the sale order."""
        self.ensure_one()
        order = self.order_id
        if order.state not in ('sale', 'delivered'):
            raise UserError(_('Only confirmed or delivered orders can be invoiced.'))
        # Mark the order as invoiced
        order.write({'state': 'invoiced'})
        order.message_post(
            body=_('Invoice created on %s') % self.invoice_date,
            subject=_('Invoice Created'),
        )
        _logger.info('Invoice created for sale order %s', order.name)
        return {'type': 'ir.actions.act_window_close'}
