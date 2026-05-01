# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class SaaSWebsitePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'saas_license_count' in counters:
            partner = request.env.user.partner_id
            values['saas_license_count'] = request.env['logismart.saas.license'].search_count([('partner_id', '=', partner.id)])
        return values

    @http.route(['/my/licenses', '/my/licenses/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_licenses(self, **kw):
        partner = request.env.user.partner_id
        licenses = request.env['logismart.saas.license'].search([('partner_id', '=', partner.id)])
        return request.render("logismart_website.portal_my_licenses", {'licenses': licenses})
