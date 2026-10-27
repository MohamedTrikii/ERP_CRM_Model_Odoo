# 📈 Flowmerce ERP — Custom Odoo 19 Modules (CRM · Sales · Purchase · eCommerce)

> A set of Odoo 19 modules covering the full **Lead → Opportunity → Quotation → Order → Invoice → Purchase** cycle, with **lead scoring**, customer segmentation, risk detection, stock-driven auto-purchasing and a SaaS-licence web shop.

🇫🇷 [Version française](README.fr.md)

![Odoo](https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-ORM-4169E1?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-blue)

---

## 🧩 Modules

| Module | Purpose | Depends on |
|---|---|---|
| [`crm_mt`](crm_mt/) | CRM pipeline, scoring, segmentation, stock simulation, automations | `base`, `mail`, `utm`, `product` |
| [`flowmerce_sale`](flowmerce_sale/) | Quotations & sales orders, margins, payment status, invoice wizard | `crm_mt`, `product`, `uom` |
| [`flowmerce_purchase`](flowmerce_purchase/) | Purchase orders, supplier scoring, delivery risk, auto-order | `crm_mt`, `product`, `uom` |
| [`logismart_website`](logismart_website/) | Website & eCommerce for SaaS licences, customer portal (`/my/licenses`), contact form → CRM lead | `website`, `website_sale`, `crm_mt` |

## ✨ Highlights

**CRM (`crm_mt`, model `crm.mt.lead`)**
- `lead_score` (0–100) computed from priority, expected revenue, activity recency, stage and partner.
- Automatic **segmentation** (VIP / Loyal / At-Risk / New / Cold) and **risk level** (Low / Medium / High).
- Kanban pipeline with stages, teams, lost reasons and chatter.
- **Stock simulation** (`crm.mt.product.stock`): available / reserved / net quantity with an automatic purchase trigger.

**Sales (`flowmerce_sale`)** — line and order **margins**, cost price auto-filled from the product, global discount, payment status (unpaid / partial / paid), automatic confirmation and invoicing, revenue & margin dashboards.

**Purchase (`flowmerce_purchase`)** — **supplier score** (0–100), **delivery-risk** prediction, auto-order flag confirmed by cron, line discounts, spend & risk dashboards.

**Automations** — scheduled actions: stale-quotation follow-up, lead-score recomputation, high-risk lead detection, low-stock check, auto-confirmation of flagged purchase orders.

**Security** — user / sales / purchase / manager groups with record rules.

## 🔁 CRM & sales process

```mermaid
flowchart TD
    A[New lead] --> B[CRM pipeline<br/>team · owner · priority]
    B --> C[Scoring, segmentation,<br/>risk detection]
    C --> D1[New] --> D2[Qualified] --> D3[Proposal] --> D4[Negotiation]
    D4 --> E{Won?}
    E -- Yes --> G[Quotation → Sales order]
    G --> H[Draft → Sent → Confirmed → Delivered → Invoiced]
    E -- No --> I[Lost + reason]
    H --> K{Low stock?}
    K -- Yes --> L[Automatic purchase order]
    L --> M[Draft → Sent → Confirmed → Received → Invoiced]
    K -- No --> N[Sale completed]
```

## 🚀 Installation

1. Copy the module folders into a directory of your Odoo 19 `addons_path`.
2. Restart Odoo, enable developer mode and click **Update Apps List**.
3. Install in this order: `crm_mt` → `flowmerce_sale` → `flowmerce_purchase` (→ `logismart_website` for the web shop).

> The custom models are namespaced (`flowmerce.sale.order`, `flowmerce.purchase.order`…), so these modules install **alongside** Odoo's official Sales and Purchase apps.

## ✅ Verified

Installed on a fresh **Odoo 19** database together with the official *Sales*, *Purchase* and *eCommerce* apps (demo data included): no error, no warning.

```bash
docker run -d --name db -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres postgres:16
docker run --rm --link db -v "$PWD:/mnt/extra-addons" odoo:19 -- -d test --with-demo --stop-after-init   -i sale_management,purchase,website_sale,crm_mt,flowmerce_sale,flowmerce_purchase,logismart_website
```

## 📁 Structure

```
crm_mt/              models · views (kanban, form, dashboards) · data (automations) · security
flowmerce_sale/      models · views · wizard · report · data (sequences, demo)
flowmerce_purchase/  models · views · data · controllers
logismart_website/   website templates · portal · SaaS licences · email templates · cron jobs
```

## 👤 Author

**Mohamed Triki** — [GitHub](https://github.com/MohamedTrikii)
