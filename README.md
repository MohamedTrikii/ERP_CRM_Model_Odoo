# erp_crm_triki

Module Odoo 19 tout-en-un : CRM, Vente, Achat

## Fonctionnalités principales
- Gestion complète du cycle Lead → Opportunité → Devis → Commande → Facturation → Achat
- Pipeline CRM dynamique (kanban, scoring, conversion, chatter)
- Workflow vente/achat complet (brouillon, envoyé, confirmé, livré, facturé, annulé)
- Calculs automatiques (taxes, remises, totaux)
- Intégration CRM-Vente-Achat
- Dashboards analytiques (KPI, graphes, pivot, calendrier)
- Sécurité avancée (groupes, accès, règles)
- Automatisations (activités, rappels, séquences, triggers)
- Tests unitaires et données de démonstration

## Structure du module
- `models/` : ORM, héritages, logique métier
- `views/` : XML (form, tree, kanban, search, dashboard)
- `security/` : ir.model.access.csv, record rules, groupes
- `data/` : séquences, données initiales, démo
- `controllers/` : endpoints REST si besoin
- `tests/` : tests unitaires Odoo

## Installation
1. Copier le dossier dans `addons/`
2. Installer via l’interface Odoo (Apps)
3. Profiter d’un ERP complet, modulaire et maintenable

## Auteur
Open Source – Triki

---

Pour toute contribution ou adaptation, respecter la structure et les bonnes pratiques Odoo.
