import frappe

frappe.init(site='frappe.com')
frappe.connect()

# 1. Module Def
if not frappe.db.exists("Module Def", "Algeria Tax"):
    m = frappe.new_doc("Module Def")
    m.module_name = "Algeria Tax"
    m.app_name = "algeria_tax"
    m.insert()
    print("Created Module Def: Algeria Tax")

# 2. Algerian Tax Settings
dt_name = "Algerian Tax Settings"
if not frappe.db.exists("DocType", dt_name):
    doc = frappe.new_doc("DocType")
    doc.name = dt_name
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.issingle = 1
    doc.track_changes = 1
    
    fields = [
        {"fieldname": "sec_ident", "label": "Identification Fiscale", "fieldtype": "Section Break"},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "nif", "label": "NIF (Numéro d'Identification Fiscale - 15 chiffres)", "fieldtype": "Data", "reqd": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "nis", "label": "NIS (Numéro d'Identification Statistique)", "fieldtype": "Data"},
        {"fieldname": "rc", "label": "Registre de Commerce (RC)", "fieldtype": "Data"},
        {"fieldname": "article_imposition", "label": "N° Article d'Imposition (AI)", "fieldtype": "Data"},
        {"fieldname": "tax_center", "label": "Centre des Impôts de Rattachement", "fieldtype": "Select", "options": "CDI (Centre des Impôts)\nDGE (Direction des Grandes Entreprises)\nCPI (Centre de Proximité des Impôts)", "default": "CDI (Centre des Impôts)"},

        {"fieldname": "sec_regime", "label": "Régime Fiscal & Taux d'IBS", "fieldtype": "Section Break"},
        {"fieldname": "activity_type", "label": "Activité Principale", "fieldtype": "Select", "options": "Commerce / Négoce (26%)\nPrestations de Services (26%)\nBTPH et Tourisme (23%)\nProduction de biens (19%)\nActivités Mixtes (Comptabilité séparée)", "default": "Prestations de Services (26%)"},
        {"fieldname": "ibs_rate", "label": "Taux d'IBS Applicable (%)", "fieldtype": "Percent", "default": "26.0"},
        {"fieldname": "min_ibs_amount", "label": "Minimum Forfaitaire IBS (DZD)", "fieldtype": "Currency", "default": "10000.0", "read_only": 1},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "exemption_program", "label": "Dispositif d'Avantage / Exonération", "fieldtype": "Select", "options": "Aucun (Régime de droit commun)\nAAPI (ex-ANDI) - Secteurs prioritaires\nAAPI - Zones Sud / Hauts-Plateaux\nNESDA (ex-ANSEJ) - Emploi jeunes\nCNAC\nANGEM\nLabel Startup / Incubateur (Décret 20-254)\nExportateur hors hydrocarbures (Art. 138-1)\nWilaya du Grand Sud (Art. 138 bis)", "default": "Aucun (Régime de droit commun)"},
        {"fieldname": "decision_number", "label": "N° Décision d'Octroi d'Avantages", "fieldtype": "Data"},
        {"fieldname": "decision_date", "label": "Date de la Décision", "fieldtype": "Date"},
        {"fieldname": "start_date", "label": "Date Début d'Exonération", "fieldtype": "Date"},
        {"fieldname": "end_date", "label": "Date Fin d'Exonération", "fieldtype": "Date"},
        {"fieldname": "current_stage", "label": "Phase Actuelle de l'Avantage", "fieldtype": "Select", "options": "Exonération Totale (100%)\nAbattement Dégressif 1ère Année (70%)\nAbattement Dégressif 2ème Année (50%)\nAbattement Dégressif 3ème Année (25%)\nRégime Normal / Expiré", "default": "Exonération Totale (100%)"},
        {"fieldname": "reinvestment_obligation", "label": "Obligation de Réinvestissement 30% (Art. 142)", "fieldtype": "Check", "default": "0"},

        {"fieldname": "sec_comptes", "label": "Comptes SCF de Liaison Fiscale", "fieldtype": "Section Break"},
        {"fieldname": "account_tva_collectee", "label": "Compte TVA Collectée", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_tva_deductible_goods", "label": "Compte TVA Déductible (Biens & Services)", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_tva_deductible_assets", "label": "Compte TVA Déductible (Immobilisations)", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_tva_credit", "label": "Compte Crédit de TVA Reportable", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_tva_due", "label": "Compte TVA à Payer", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "col_3", "fieldtype": "Column Break"},
        {"fieldname": "account_irg_salaries", "label": "Compte IRG Salaires Retenu", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_ibs_installments", "label": "Compte Acomptes IBS", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_ibs_due", "label": "Compte IBS Dû", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_reinvestment_reserve", "label": "Compte Réserve Réinvestissement", "fieldtype": "Link", "options": "Account"},
        {"fieldname": "account_cash", "label": "Compte Caisse Espèces", "fieldtype": "Link", "options": "Account"}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1})
    doc.insert()
    print("Created DocType: Algerian Tax Settings")
else:
    print("DocType Algerian Tax Settings already exists")

# 3. Attestation Franchise TVA (C20)
dt_c20 = "Attestation Franchise TVA"
if not frappe.db.exists("DocType", dt_c20):
    doc = frappe.new_doc("DocType")
    doc.name = dt_c20
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.autoname = "field:attestation_number"
    doc.track_changes = 1
    
    fields = [
        {"fieldname": "attestation_number", "label": "N° Attestation C20 (Visa CDI)", "fieldtype": "Data", "reqd": 1, "unique": 1},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "program_type", "label": "Dispositif d'Origine", "fieldtype": "Select", "options": "AAPI (ex-ANDI)\nExportateur Hors Hydrocarbures\nSecteur Spécifique", "default": "AAPI (ex-ANDI)"},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "visa_date", "label": "Date de Délivrance / Visa CDI", "fieldtype": "Date", "reqd": 1},
        {"fieldname": "expiry_date", "label": "Date d'Expiration", "fieldtype": "Date", "reqd": 1},
        {"fieldname": "status", "label": "Statut", "fieldtype": "Select", "options": "Active\nÉpuisée\nExpirée\nSuspendue", "default": "Active"},

        {"fieldname": "sec_contingent", "label": "Gestion du Contingent en Franchise", "fieldtype": "Section Break"},
        {"fieldname": "contingent_total_ht", "label": "Contingent Total Autorisé (DZD HT)", "fieldtype": "Currency", "reqd": 1},
        {"fieldname": "contingent_consomme_ht", "label": "Contingent Consommé (DZD HT)", "fieldtype": "Currency", "default": "0", "read_only": 1},
        {"fieldname": "col_2", "fieldtype": "Column Break"},
        {"fieldname": "contingent_disponible_ht", "label": "Solde Disponible en Franchise (DZD HT)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "notes", "label": "Observations & Références Dossier", "fieldtype": "Small Text"}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1})
    doc.insert()
    print("Created DocType: Attestation Franchise TVA")
else:
    print("DocType Attestation Franchise TVA already exists")

frappe.db.commit()
print("Phase 1 DocTypes creation complete!")
