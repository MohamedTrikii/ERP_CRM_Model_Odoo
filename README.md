# Flowmerce ERP — Odoo 19 Custom Modules

> **Professional SaaS ERP** built on Odoo 19 — intelligent, automated, production-ready.

## Modules

### `crm_mt` — CRM & Pipeline (Flowmerce AI)
- **Depends**: `base`, `mail`, `utm`, `product`
**Models**: `CRM_IIT_TRIKI`, `crm.mt.team`, `crm.mt.stage`, `crm.mt.lost.reason`, `crm.mt.sale`, `crm.mt.sale.line`, `crm.mt.purchase`, `crm.mt.purchase.line`, `crm.mt.product.stock`
**AI Features**:
  - `lead_score` (0–100): computed from priority, revenue, activity recency, stage, partner
  - `segment_client`: VIP / Loyal / At-Risk / New / Cold (auto-computed)
  - `risk_level`: Low / Medium / High (auto-computed)
  - `days_since_activity` / `last_activity_date`
  - `compute_score()`, `compute_probability()`, `detect_risk()` — public AI methods
- **Stock Simulation**: `crm.mt.product.stock` — qty_available, qty_reserved, qty_net, auto-purchase trigger
- **Automations**: 5 cron jobs + 5 server actions (inactive leads, low stock, stale quotations, PO auto-confirm, score recompute)
- **Security**: `group_flowmerce_user`, `group_flowmerce_sales`, `group_flowmerce_purchase`, `group_flowmerce_manager` + record rules

### `sale` — Sales Management (Flowmerce)
- **Depends**: `base`, `mail`, `product`, `uom`, `crm_mt`
- **Models**: `sale.order`, `sale.order.line`, `res.partner` (extension), `sale.invoice.wizard`
- **New Fields**:
  - `margin` / `margin_rate` (computed per line and per order)
  - `cost_price` on lines (auto-filled from product)
  - `discount_global` — order-level additional discount
  - `payment_status`: Unpaid / Partially Paid / Paid
- **Methods**: `compute_margin()`, `action_confirm_auto()`, `generate_invoice_auto()`, `action_mark_paid()`, `cron_auto_followup_quotations()`
- **Dashboard**: graph (revenue/margin by month), pivot (salesperson analysis)

### `purchase` — Purchase Management (Flowmerce)
- **Depends**: `base`, `mail`, `product`, `uom`, `crm_mt`
- **Models**: `purchase.order`, `purchase.order.line`
- **New Fields**:
  - `supplier_score` (0–100, computed)
  - `delay_risk`: Low / Medium / High (computed)
  - `auto_order_flag`: enables auto-confirm via cron
  - `expected_delivery_date` / `actual_delivery_date`
  - `discount` on order lines
- **Methods**: `evaluate_supplier()`, `auto_create_purchase_if_needed()`
- **Dashboard**: spend by supplier, delivery risk distribution, pivot analysis

---

## 🔁 **Schéma Processus CRM & Ventes**

```mermaid
flowchart TD

%% Début
A[Début : Nouveau Lead]

%% Qualification du Lead
A --> B[Entrée dans le pipeline CRM<br>Attribuer équipe, responsable, priorité]
B --> C[Scoring IA, segmentation automatique,<br>détection de risque]

%% Pipeline (Etapes du Kanban)
C --> D1[Etape : Nouveau]
D1 --> D2[Etape : Qualifié]
D2 --> D3[Etape : Proposition]
D3 --> D4[Etape : Négociation]

%% 1. Cas Gagné
D4 --> E{Deal gagné ?}
E -- Oui --> F[Mark 'Gagné', convertir le lead<br>en commande de vente]

%% Conversion Devis → Commande
F --> G[Créer Devis CRM<br>Associer lignes produits & montant]
G --> H[Workflow vente :<br>Brouillon → Envoyé → Confirmé → Livré → Facturé]

%% 2. Cas Perte
E -- Non --> I[Mark 'Perdu'<br>enregistrer raison de perte<br>(ex : trop cher, concurrent, pas de réponse)]

%% 3. Automatisations & relances
D1 --> J[Déclencher automations :<br>- Relance emails/tâches (cron)<br>- Recalcule scoring<br>- Passage automatique étape (si critère atteint)<br>- Relance inactivité]
D2 --> J
D3 --> J
D4 --> J

%% 4. Cas Achat Automatique (stock)
H --> K{Stock faible ?}
K -- Oui --> L[Générer auto-commande achat CRM]
L --> M[Workflow achat :<br>Brouillon → Envoyé → Confirmé → Reçu → Facturé]
K -- Non --> N[Fin vente]

%% Fin
I --> FIN1([Fin du cycle - lead perdu])
M --> FIN2([Fin du cycle - achat/vente complété])
N --> FIN3([Fin du cycle - vente complétée])
```

---

## Installation Order
1. `crm_mt` — base module (no custom deps)
2. `sale` — depends on crm_mt
3. `purchase` — depends on crm_mt

## Odoo Version
- **Target**: Odoo 19.0
- **License**: LGPL-3

## Architecture Summary
```
crm_mt/
  models/
    crm_mt_lead.py (model: CRM_IIT_TRIKI)          ← AI scoring, segmentation, risk detection
    crm_mt_product_stock.py ← Stock simulation + auto-purchase
  data/
    crm_mt_automation.xml   ← 5 cron jobs + 5 server actions
  security/
    crm_mt_security.xml     ← Groups + record rules
  views/
    crm_mt_lead_views.xml   ← Enhanced kanban + form + list + search
    crm_mt_dashboard_views.xml ← CRM + Stock dashboards

sale/
  models/
    sale_order.py           ← +margin, +payment_status, +auto actions
    sale_order_line.py      ← +cost_price, +margin, +margin_rate
  views/
    sale_order_views.xml    ← Enhanced with margin KPIs
    sale_dashboard_views.xml ← Revenue/margin dashboards

purchase/
  models/
    purchase_order.py       ← +supplier_score, +delay_risk, +auto_order
    purchase_order_line.py  ← +discount
  views/
    purchase_order_views.xml   ← Supplier intelligence KPI banner
    purchase_dashboard_views.xml ← Spend & risk dashboards
```

## Author
Flowmerce ERP — Open Source (Triki)

- **Depends**: `base`, `mail`, `utm`, `product`
- **Models**: `CRM_IIT_TRIKI`, `crm.mt.team`, `crm.mt.stage`, `crm.mt.lost.reason`, `crm.mt.sale`, `crm.mt.sale.line`, `crm.mt.purchase`, `crm.mt.purchase.line`
- **Features**: Lead/Opportunity pipeline, Sales & Purchase pipelines with full workflow

### `sale` — Sales Order Management
- **Depends**: `base`, `mail`, `product`, `uom`, `crm_mt`
- **Models**: `sale.order`, `sale.order.line`, `res.partner` (extension), `sale.invoice.wizard`
- **Features**: Quotations and Sales Orders with workflow, Invoice wizard, Customer statistics

### `purchase` — Purchase Order Management
- **Depends**: `base`, `mail`, `product`, `uom`, `crm_mt`
- **Models**: `purchase.order`, `purchase.order.line`
- **Features**: RFQ and Purchase Orders with full workflow (draft → sent → purchase → received → invoiced)

## Installation Order
1. `crm_mt` (no custom deps)
2. `sale` (depends on crm_mt)
3. `purchase` (depends on crm_mt)

## Odoo Version
- **Target**: Odoo 19.0
- **License**: LGPL-3

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
