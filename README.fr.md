# 📈 Flowmerce ERP — Modules Odoo 19 (CRM · Ventes · Achats · eCommerce)

> Un ensemble de modules Odoo 19 qui couvre tout le cycle **Lead → Opportunité → Devis → Commande → Facture → Achat**, avec **scoring des leads**, segmentation client, détection de risque, réapprovisionnement automatique selon le stock et boutique en ligne de licences SaaS.

🇬🇧 [English version](README.md)

![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ORM-4169E1?logo=postgresql&logoColor=white)
![Licence](https://img.shields.io/badge/Licence-LGPL--3-blue)

---

## 🧩 Modules

| Module | Rôle | Dépend de |
|---|---|---|
| [`crm_mt`](crm_mt/) | Pipeline CRM, scoring, segmentation, simulation de stock, automatisations | `base`, `mail`, `utm`, `product` |
| [`flowmerce_sale`](flowmerce_sale/) | Devis et commandes, marges, statut de paiement, assistant de facturation | `crm_mt`, `product`, `uom` |
| [`flowmerce_purchase`](flowmerce_purchase/) | Commandes fournisseurs, score fournisseur, risque de retard, commande automatique | `crm_mt`, `product`, `uom` |
| [`logismart_website`](logismart_website/) | Site web et eCommerce de licences SaaS, portail client (`/my/licenses`), formulaire de contact → lead CRM | `website`, `website_sale`, `crm_mt` |

## ✨ Points forts

**CRM (`crm_mt`, modèle `crm.mt.lead`)**
- `lead_score` (0–100) calculé à partir de la priorité, du revenu attendu, de la date de dernière activité, de l'étape et du partenaire.
- **Segmentation** automatique (VIP / Fidèle / À risque / Nouveau / Froid) et **niveau de risque** (faible / moyen / élevé).
- Pipeline kanban avec étapes, équipes, raisons de perte et chatter.
- **Simulation de stock** (`crm.mt.product.stock`) : quantités disponible / réservée / nette, avec déclenchement automatique d'un achat.

**Ventes (`flowmerce_sale`)** : **marges** par ligne et par commande, prix de revient repris du produit, remise globale, statut de paiement (non payé / partiel / payé), confirmation et facturation automatiques, tableaux de bord chiffre d'affaires et marge.

**Achats (`flowmerce_purchase`)** : **score fournisseur** (0–100), estimation du **risque de retard**, commande automatique confirmée par une tâche planifiée, remises par ligne, tableaux de bord des dépenses et des risques.

**Automatisations** : tâches planifiées de relance des devis en attente, recalcul des scores, détection des leads à risque, contrôle du stock bas, confirmation automatique des commandes fournisseurs marquées.

**Sécurité** : groupes utilisateur / ventes / achats / manager avec règles d'enregistrement.

## 🔁 Processus CRM et ventes

```mermaid
flowchart TD
    A[Nouveau lead] --> B[Pipeline CRM<br/>équipe · responsable · priorité]
    B --> C[Scoring, segmentation,<br/>détection de risque]
    C --> D1[Nouveau] --> D2[Qualifié] --> D3[Proposition] --> D4[Négociation]
    D4 --> E{Gagné ?}
    E -- Oui --> G[Devis → Commande]
    G --> H[Brouillon → Envoyé → Confirmé → Livré → Facturé]
    E -- Non --> I[Perdu + raison]
    H --> K{Stock bas ?}
    K -- Oui --> L[Commande fournisseur automatique]
    L --> M[Brouillon → Envoyé → Confirmé → Reçu → Facturé]
    K -- Non --> N[Vente terminée]
```

## 🚀 Installation

1. Copier les dossiers des modules dans un répertoire de l'`addons_path` d'Odoo 19.
2. Redémarrer Odoo, activer le mode développeur puis **Mettre à jour la liste des applications**.
3. Installer dans l'ordre : `crm_mt` → `flowmerce_sale` → `flowmerce_purchase` (→ `logismart_website` pour la boutique en ligne).

> Les modèles personnalisés ont leur propre espace de noms (`flowmerce.sale.order`, `flowmerce.purchase.order`…) : ces modules s'installent **à côté** des applications officielles Ventes et Achats d'Odoo.

## ✅ Vérifié

Installé sur une base **Odoo 19** neuve avec les applications officielles *Ventes*, *Achats* et *eCommerce* (données de démo comprises) : aucune erreur, aucun avertissement.

```bash
docker run -d --name db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:16
docker run --rm --link db -v "$PWD:/mnt/extra-addons" odoo:19 -- -d test --with-demo --stop-after-init   -i sale_management,purchase,website_sale,crm_mt,flowmerce_sale,flowmerce_purchase,logismart_website
```

## 📁 Structure

```
crm_mt/              modèles · vues (kanban, formulaire, tableaux de bord) · données (automatisations) · sécurité
flowmerce_sale/      modèles · vues · assistant · rapport · données (séquences, démo)
flowmerce_purchase/  modèles · vues · données · contrôleurs
logismart_website/   modèles de pages web · portail · licences SaaS · modèles d'e-mail · tâches planifiées
```

## 👤 Auteur

**Mohamed Triki** — [GitHub](https://github.com/MohamedTrikii)
