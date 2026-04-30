# Changelog

## [1.0.0] - 2026-04-29

### Added
- Module CRM MT complet avec toutes les fonctionnalités
- Gestion des leads et opportunités
- Gestion des équipes de vente
- Stages personnalisables avec couleurs
- Raisons de perte (Lost Reasons)
- Commandes de vente avec lignes
- Commandes d'achat avec lignes
- Vues Kanban, List, Form, Graph, Pivot pour tous les modèles
- Intégration complète avec le chatter
- Tracking des activités
- Séquences automatiques pour les commandes
- Données par défaut (stages et lost reasons)
- Documentation complète

### Fixed
- Correction de la structure XML dans crm_mt_sale_views.xml
- Suppression du code dupliqué dans crm_mt_purchase_views.xml
- Correction du filtre "My Team Leads" dans crm_mt_lead_views.xml (supprimé car le champ user.team_id n'existe pas)
- Ajout du champ "color" aux modèles crm.mt.sale et crm.mt.purchase
- Correction de l'onchange product_id dans crm.mt.purchase.line

### Changed
- Amélioration du manifest avec description détaillée
- Organisation des fichiers de données dans le bon ordre
- Amélioration des droits d'accès
