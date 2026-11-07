# Guide Officiel d'Installation & d'Exploitation — El Tassyir El Ali (التسيير الآلي)

**Solution Intégrée de Comptabilité SCF, Fiscalité DGI (G50 / Liasse G n°4), Paie Algérienne 3-Strates (CNAS / IRG / G29), Virements Bancaires EDI & Cockpit Expert-Comptable / Commissaire aux Comptes (CAC)**

---

## 1. Prérequis Serveur (Ubuntu 22.04 LTS ou 24.04 LTS — Jusqu'à 10 Dossiers Clients / PME)

- **Processeur** : 4 vCPU minimum (8 vCPU recommandé pour 10 sites PME).
- **Mémoire RAM** : 8 Go à 16 Go RAM.
- **Disque** : 120 Go SSD NVMe.
- **Stack Logicielle** : Python `3.11+`, Node.js `18+`, MariaDB `10.6+`, Redis `7+`, `wkhtmltopdf` (avec `qt` patché), `frappe-bench` v15.

---

## 2. Installation Pas-à-Pas sur un Nouveau Serveur

### Étape 2.1 — Appliquer la Configuration Optimisée MariaDB 10.6
Copiez le fichier [`config/99-frappe-mariadb.cnf`](config/99-frappe-mariadb.cnf) dans `/etc/mysql/mariadb.conf.d/99-frappe.cnf` puis redémarrez MariaDB :

```bash
sudo cp config/99-frappe-mariadb.cnf /etc/mysql/mariadb.conf.d/99-frappe.cnf
sudo systemctl restart mariadb
```

### Étape 2.2 — Initialiser le Bench Frappe v15 et Récupérer vos 2 Dépôts GitHub (`bsn-web`)

```bash
# 1. Créer le bench Frappe en branche version-15
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench

# 2. Télécharger ERPNext v15 depuis votre fork officiel bsn-web
bench get-app https://github.com/bsn-web/erpnext.git --branch version-15

# 3. Télécharger l'application HRMS v15 (Paie & RH)
bench get-app hrms --branch version-15

# 4. Télécharger votre solution privée El Tassyir El Ali (algeria_tax)
bench get-app https://github.com/bsn-web/algeria_tax.git --branch main
```

### Étape 2.3 — Créer le Site du Cabinet ou d'une Entreprise Cliente

```bash
# 1. Créer le site (ex: cabinet.eltassyir.dz)
bench new-site cabinet.eltassyir.dz --mariadb-root-password VOTRE_MOT_DE_PASSE_SQL --admin-password VOTRE_MOT_DE_PASSE_ADMIN

# 2. Installer ERPNext, HRMS et El Tassyir El Ali (algeria_tax)
bench --site cabinet.eltassyir.dz install-app erpnext
bench --site cabinet.eltassyir.dz install-app hrms
bench --site cabinet.eltassyir.dz install-app algeria_tax

# 3. Exécuter la migration et compiler les assets (Logo SVG, Thème UI, JS Algérie)
bench --site cabinet.eltassyir.dz migrate
bench build --app algeria_tax
bench --site cabinet.eltassyir.dz clear-cache
```

---

## 3. Ce qui est Configuré et Verrouillé Automatiquement dès l'Installation (`after_install` / `after_migrate`)

1. **Verrouillage Strict « Algérie Uniquement » (`Country = Algeria` & `Currency = DZD`)** :
   - Toute création d'entreprise (`Company`) est automatiquement verrouillée sur le pays **`Algeria`** (`الجزائر`) et la devise **`DZD`** (Dinar Algérien). Toute tentative de création d'une société dans un autre pays ou une autre devise est bloquée par le contrôleur serveur et client.
2. **Chargement Automatique du Référentiel National Algérien (`algerian_registry.py`)** :
   - **22 Banques Algériennes + CCP Algérie Poste + Trésor Public** pré-chargées avec leurs codes BA à 3 chiffres (`001` BNA à `029` Arab Bank) et codes SWIFT/BIC.
   - **18 Compagnies d'Assurances Algériennes (CNA/UAR)** : SAA, CAAR, CAAT, CASH, CIAR, Alliance, Trust, Salama, GAM, GIG, TALA, CAARAMA, Macir Vie, Cardif, El Djazaïr Takaful, CAGEX, SGCI, CCR.
   - **7 Organismes Sociaux & Parafiscaux** : CNAS (9% + 26% = 35%), CASNOS (15%), CACOBATPH (12,96%), FNPOS, CNAC, ONAAPH, Taxe Formation/Apprentissage.
   - **58 Wilayas d'Algérie (`01` Adrar à `58` El Meniaa)** avec zonage Nord / Hauts-Plateaux / Sud / Grand Sud.
3. **10 Index Composites MariaDB** :
   - Créés automatiquement sur `tabAccount`, `tabPayment Entry`, `tabSales Invoice`, `tabPurchase Invoice`, `tabLead`, `tabEmployee`, `tabG50 Declaration`, `tabBilan Fiscal`, `tabCNAS Declaration`, `tabG29 Declaration`.
4. **Identité Visuelle « El Tassyir El Ali — التسيير الآلي » & Traductions FR / AR** :
   - Logo vectoriel comptabilité/audit (`/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg`), thème moderne `profi_theme.css` et dictionnaires de traductions terminologiques algériennes (`fr.csv` & `ar.csv`).
