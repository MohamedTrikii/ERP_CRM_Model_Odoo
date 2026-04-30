# CRM MT Module - Custom CRM for Odoo 19

## Description
Module CRM complet avec gestion des leads, opportunités, équipes de vente, commandes de vente et d'achat.

## Fonctionnalités

### 1. Gestion des Leads/Opportunités
- Pipeline de vente avec stages personnalisables
- Gestion de la priorité (Normal, Important, Urgent)
- Probabilité de closing et revenu attendu
- Vue Kanban, Form, List, Graph, Pivot
- Actions automatiques (Won, Lost, Create Quotation)

### 2. Gestion des Équipes
- Création d'équipes de vente
- Assignation de leaders et membres
- Filtrage des leads par équipe

### 3. Commandes de Vente
- Création de commandes depuis les leads
- Gestion des lignes de commande
- États : Brouillon, Envoyé, Confirmé, Livré, Facturé
- Calcul automatique des totaux

### 4. Commandes d'Achat
- Gestion des commandes fournisseurs
- Workflow complet : Brouillon → Envoyé → Confirmé → Reçu → Facturé
- Lignes de commande avec produits

### 5. Configuration
- Stages personnalisables avec couleurs
- Raisons de perte (Lost Reasons)
- Séquences automatiques pour les commandes

## Installation

1. Copiez le module dans le dossier addons d'Odoo
2. Mettez à jour la liste des applications
3. Installez le module "CRM MT"

## Configuration

### Étapes Initiales
1. Allez dans CRM MT > Configuration > Stages
2. Créez les stages de votre pipeline (ex: Nouveau, Qualifié, Proposition, Négociation, Gagné, Perdu)
3. Créez vos équipes de vente dans Configuration > Teams
4. Définissez les raisons de perte dans Configuration > Lost Reasons

## Utilisation

### Créer un Lead
1. Allez dans CRM MT > Leads/Opportunities
2. Cliquez sur "Create"
3. Remplissez les informations du lead
4. Assignez une équipe et un responsable

### Convertir un Lead en Commande
1. Ouvrez un lead
2. Cliquez sur "Create Quotation"
3. Le lead sera converti en commande de vente

## Structure Technique

### Modèles
- `crm.mt.lead` - Leads et opportunités
- `crm.mt.team` - Équipes de vente
- `crm.mt.stage` - Stages du pipeline
- `crm.mt.lost.reason` - Raisons de perte
- `crm.mt.sale` - Commandes de vente
- `crm.mt.sale.line` - Lignes de commande de vente
- `crm.mt.purchase` - Commandes d'achat
- `crm.mt.purchase.line` - Lignes de commande d'achat

### Dépendances
- `base` - Module de base Odoo
- `mail` - Messagerie et chatter
- `utm` - Tracking UTM
- `product` - Gestion des produits

## Droits d'Accès

Deux niveaux d'accès :
- **User** (`base.group_user`) : Lecture, écriture, création, suppression
- **Manager** (`base.group_system`) : Tous les droits

## Support

Pour toute question ou problème, consultez la documentation Odoo ou contactez votre administrateur système.

## Auteur

Open Source

## Licence

LGPL-3
