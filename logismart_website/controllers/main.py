# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class LogiSmartContact(http.Controller):

    @http.route('/contactus', type='http', auth="public", website=True, sitemap=True)
    def contactus(self, **kw):
        return request.render("logismart_website.contact_page_template", {})

    @http.route('/contact/submit', type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        # Création du Lead dans le CRM LogiSmart
        lead = request.env['crm.mt.lead'].sudo().create({
            'name': f"Demande Site Web: {post.get('subject', 'Sans objet')}",
            'partner_name': post.get('name'),
            'email_from': post.get('email'),
            'phone': post.get('phone'),
            'description': post.get('message'),
            'priority': '1', # Prospect à suivre
        })
        
        # Déclenchement du calcul du score IA
        lead.compute_score()
        
        return request.render("logismart_website.contact_thanks_template", {'lead': lead})
