from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    # Champs personnalisés pour centralisation client
    crm_lead_count = fields.Integer('Leads/Opportunities', compute='_compute_crm_lead_count')
    sale_order_count = fields.Integer('Sale Orders', compute='_compute_sale_order_count')
    purchase_order_count = fields.Integer('Purchase Orders', compute='_compute_purchase_order_count')

    def _compute_crm_lead_count(self):
        for partner in self:
            partner.crm_lead_count = self.env['crm.lead'].search_count([('partner_id', '=', partner.id)])

    def _compute_sale_order_count(self):
        for partner in self:
            partner.sale_order_count = self.env['sale.order'].search_count([('partner_id', '=', partner.id)])

    def _compute_purchase_order_count(self):
        for partner in self:
            partner.purchase_order_count = self.env['purchase.order'].search_count([('partner_id', '=', partner.id)])
