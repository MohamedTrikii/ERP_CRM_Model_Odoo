from odoo import http
from odoo.http import request

class CrmDashboardController(http.Controller):
    @http.route('/crm/dashboard', auth='user', website=True)
    def crm_dashboard(self, **kw):
        lead_count = request.env['crm.lead'].search_count([])
        return request.render('erp_crm_triki.crm_dashboard_template', {
            'lead_count': lead_count,
        })

class SaleDashboardController(http.Controller):
    @http.route('/sale/dashboard', auth='user', website=True)
    def sale_dashboard(self, **kw):
        sale_count = request.env['sale.order'].search_count([])
        return request.render('erp_crm_triki.sale_dashboard_template', {
            'sale_count': sale_count,
        })

class PurchaseDashboardController(http.Controller):
    @http.route('/purchase/dashboard', auth='user', website=True)
    def purchase_dashboard(self, **kw):
        purchase_count = request.env['purchase.order'].search_count([])
        return request.render('erp_crm_triki.purchase_dashboard_template', {
            'purchase_count': purchase_count,
        })
