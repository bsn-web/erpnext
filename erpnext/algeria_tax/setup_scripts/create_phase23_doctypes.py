import frappe

frappe.init(site='frappe.com')
frappe.connect()

# 1. G50 Tax Line (Child Table)
dt_line = "G50 Tax Line"
if not frappe.db.exists("DocType", dt_line):
    doc = frappe.new_doc("DocType")
    doc.name = dt_line
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.istable = 1
    
    fields = [
        {"fieldname": "tax_name", "label": "Désignation de la Taxe / Impôt", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
        {"fieldname": "tax_category", "label": "Catégorie", "fieldtype": "Select", "options": "TVA Collectée\nTVA Déductible\nIRG Salaires\nRetenues Diverses\nDroit de Timbre", "reqd": 1, "in_list_view": 1},
        {"fieldname": "base_amount", "label": "Base Imposable (DZD)", "fieldtype": "Currency", "in_list_view": 1},
        {"fieldname": "tax_rate", "label": "Taux (%)", "fieldtype": "Percent", "in_list_view": 1},
        {"fieldname": "tax_amount", "label": "Montant de l'Impôt (DZD)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1},
        {"fieldname": "account", "label": "Compte SCF Associé", "fieldtype": "Link", "options": "Account", "in_list_view": 1}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.insert()
    print("Created DocType: G50 Tax Line")
else:
    print("DocType G50 Tax Line already exists")

# 2. G50 Declaration
dt_g50 = "G50 Declaration"
if not frappe.db.exists("DocType", dt_g50):
    doc = frappe.new_doc("DocType")
    doc.name = dt_g50
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.autoname = "DECL-G50-.YYYY.-.MM.-.###"
    doc.track_changes = 1
    
    fields = [
        {"fieldname": "sec_header", "label": "Période & Identification", "fieldtype": "Section Break"},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "declaration_month", "label": "Mois Déclaré", "fieldtype": "Select", "options": "01 - Janvier\n02 - Février\n03 - Mars\n04 - Avril\n05 - Mai\n06 - Juin\n07 - Juillet\n08 - Août\n09 - Septembre\n10 - Octobre\n11 - Novembre\n12 - Décembre", "reqd": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "fiscal_year", "label": "Exercice Fiscal", "fieldtype": "Link", "options": "Fiscal Year", "reqd": 1},
        {"fieldname": "posting_date", "label": "Date de Déclaration", "fieldtype": "Date", "default": "Today", "reqd": 1},
        {"fieldname": "status", "label": "Statut", "fieldtype": "Select", "options": "Brouillon\nCalculé\nValidé & Comptabilisé\nDéposé Jibayatic", "default": "Brouillon"},

        {"fieldname": "sec_tva_collectee", "label": "1. Taxe sur la Valeur Ajoutée (TVA Collectée)", "fieldtype": "Section Break"},
        {"fieldname": "ca_taxable_19", "label": "CA Taxable à 19% (DZD HT)", "fieldtype": "Currency"},
        {"fieldname": "tva_collectee_19", "label": "TVA Facturée à 19% (DZD)", "fieldtype": "Currency"},
        {"fieldname": "ca_taxable_9", "label": "CA Taxable à 9% (DZD HT)", "fieldtype": "Currency"},
        {"fieldname": "tva_collectee_9", "label": "TVA Facturée à 9% (DZD)", "fieldtype": "Currency"},
        {"fieldname": "col_tva_col", "fieldtype": "Column Break"},
        {"fieldname": "ca_exonere_franchise", "label": "CA Exonéré / Franchise (DZD HT)", "fieldtype": "Currency"},
        {"fieldname": "total_tva_collectee", "label": "Total TVA Collectée (DZD)", "fieldtype": "Currency", "read_only": 1},

        {"fieldname": "sec_tva_deductible", "label": "2. Taxe sur la Valeur Ajoutée (TVA Déductible & Solde)", "fieldtype": "Section Break"},
        {"fieldname": "tva_deductible_goods", "label": "TVA Déductible s/ Achats Biens & Services (DZD)", "fieldtype": "Currency"},
        {"fieldname": "tva_deductible_assets", "label": "TVA Déductible s/ Immobilisations (DZD)", "fieldtype": "Currency"},
        {"fieldname": "tva_credit_reporte_anterior", "label": "Crédit de TVA Antérieur Reporté (DZD)", "fieldtype": "Currency"},
        {"fieldname": "col_tva_ded", "fieldtype": "Column Break"},
        {"fieldname": "total_tva_deductible", "label": "Total TVA Déductible & Crédits (DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "tva_nette_a_payer", "label": "TVA NETTE À PAYER (DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "tva_nouveau_credit", "label": "Nouveau Crédit de TVA à Reporter (DZD)", "fieldtype": "Currency", "read_only": 1},

        {"fieldname": "sec_ras", "label": "3. Retenues à la Source, IRG Salaires & Droits de Timbre", "fieldtype": "Section Break"},
        {"fieldname": "masse_salariale_imposable", "label": "Masse Salariale Brute Imposable (DZD)", "fieldtype": "Currency"},
        {"fieldname": "irg_salaries_retenu", "label": "IRG / Traitements & Salaires (DZD)", "fieldtype": "Currency"},
        {"fieldname": "col_ras", "fieldtype": "Column Break"},
        {"fieldname": "irg_honoraires_10", "label": "IRG / Honoraires (10%) (DZD)", "fieldtype": "Currency"},
        {"fieldname": "irg_dividendes_15", "label": "IRG / Dividendes (15%) (DZD)", "fieldtype": "Currency"},
        {"fieldname": "droit_de_timbre_especes", "label": "Droit de Timbre s/ Espèces 1% (DZD)", "fieldtype": "Currency"},

        {"fieldname": "sec_total", "label": "4. Récapitulatif des Droits Dus (Total G50)", "fieldtype": "Section Break"},
        {"fieldname": "total_g50_a_payer", "label": "TOTAL GÉNÉRAL À PAYER AU CDI (DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "journal_entry_cloture", "label": "Écriture de Clôture TVA Générée", "fieldtype": "Link", "options": "Journal Entry", "read_only": 1},

        {"fieldname": "sec_detail", "label": "Détail Analytique des Lignes de Taxe", "fieldtype": "Section Break"},
        {"fieldname": "tax_lines", "label": "Lignes de Déclaration", "fieldtype": "Table", "options": "G50 Tax Line"}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1})
    doc.insert()
    print("Created DocType: G50 Declaration")
else:
    print("DocType G50 Declaration already exists")

# 3. IBS Installment Schedule
dt_ibs = "IBS Installment Schedule"
if not frappe.db.exists("DocType", dt_ibs):
    doc = frappe.new_doc("DocType")
    doc.name = dt_ibs
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.autoname = "IBS-SCHED-.YYYY.-.###"
    doc.track_changes = 1
    
    fields = [
        {"fieldname": "sec_header", "label": "Exercice & Base N-1", "fieldtype": "Section Break"},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "fiscal_year", "label": "Exercice d'Application", "fieldtype": "Link", "options": "Fiscal Year", "reqd": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "reference_ibs_n1", "label": "Montant IBS de Référence (Exercice N-1)", "fieldtype": "Currency", "reqd": 1},
        {"fieldname": "is_first_year_exempt", "label": "Dispense 1ère Année de Création (Art. 356)", "fieldtype": "Check", "default": "0"},

        {"fieldname": "sec_acomptes", "label": "Échéancier des 3 Acomptes Provisionnels (30% chacun)", "fieldtype": "Section Break"},
        {"fieldname": "acompte_1_amount", "label": "1er Acompte (30%) - 20 Mars", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "acompte_1_paid", "label": "1er Acompte Acquitté", "fieldtype": "Check", "default": "0"},
        {"fieldname": "col_ac1", "fieldtype": "Column Break"},
        {"fieldname": "acompte_2_amount", "label": "2ème Acompte (30%) - 20 Juin", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "acompte_2_paid", "label": "2ème Acompte Acquitté", "fieldtype": "Check", "default": "0"},
        {"fieldname": "col_ac2", "fieldtype": "Column Break"},
        {"fieldname": "acompte_3_amount", "label": "3ème Acompte (30%) - 20 Novembre", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "acompte_3_paid", "label": "3ème Acompte Acquitté", "fieldtype": "Check", "default": "0"},

        {"fieldname": "sec_solde", "label": "Liquidation & Solde Définitif (20 Mai N+1)", "fieldtype": "Section Break"},
        {"fieldname": "actual_ibs_due", "label": "IBS Réel Définitif de l'Exercice (Tableau 9)", "fieldtype": "Currency"},
        {"fieldname": "total_acomptes_paid", "label": "Total des Acomptes Versés", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "col_solde", "fieldtype": "Column Break"},
        {"fieldname": "solde_a_payer", "label": "Solde Net d'IBS à Payer (au 20 Mai)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "credit_ibs_reportable", "label": "Excédent de Versement (Crédit d'IBS Reportable)", "fieldtype": "Currency", "read_only": 1}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1})
    doc.insert()
    print("Created DocType: IBS Installment Schedule")
else:
    print("DocType IBS Installment Schedule already exists")

# 4. Fiscal Table 9 Engine
dt_tab9 = "Fiscal Table 9 Engine"
if not frappe.db.exists("DocType", dt_tab9):
    doc = frappe.new_doc("DocType")
    doc.name = dt_tab9
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.autoname = "TAB9-ENG-.YYYY.-.###"
    doc.track_changes = 1
    
    fields = [
        {"fieldname": "sec_header", "label": "Exercice & Résultat Comptable", "fieldtype": "Section Break"},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "fiscal_year", "label": "Exercice Fiscal", "fieldtype": "Link", "options": "Fiscal Year", "reqd": 1},
        {"fieldname": "accounting_result_net", "label": "Résultat Net Comptable de l'Exercice (DZD)", "fieldtype": "Currency", "reqd": 1},
        {"fieldname": "col_1", "fieldtype": "Column Break"},
        {"fieldname": "ibs_rate", "label": "Taux d'IBS Applicable (%)", "fieldtype": "Percent", "default": "26.0"},
        {"fieldname": "min_ibs", "label": "Minimum de Perception Légal", "fieldtype": "Currency", "default": "10000.0", "read_only": 1},

        {"fieldname": "sec_reint", "label": "1. Réintégrations Fiscales (Charges non admises en déduction)", "fieldtype": "Section Break"},
        {"fieldname": "reint_amendes", "label": "Amendes et Pénalités Fiscales / Retard (DZD)", "fieldtype": "Currency"},
        {"fieldname": "reint_excedent_amort_vehicules", "label": "Excédent Amortissement Véhicules Tourisme > 3M (DZD)", "fieldtype": "Currency"},
        {"fieldname": "reint_provisions_sans_justice", "label": "Provisions Créances sans Action Judiciaire (DZD)", "fieldtype": "Currency"},
        {"fieldname": "col_reint", "fieldtype": "Column Break"},
        {"fieldname": "reint_charges_especes", "label": "Achats / Charges Réglées en Espèces > 1M DZD (DZD)", "fieldtype": "Currency"},
        {"fieldname": "reint_autres", "label": "Autres Charges Non Déductibles (Cadeaux, Réceptions) (DZD)", "fieldtype": "Currency"},
        {"fieldname": "total_reintegrations", "label": "TOTAL DES RÉINTÉGRATIONS (DZD)", "fieldtype": "Currency", "read_only": 1},

        {"fieldname": "sec_deduct", "label": "2. Déductions Fiscales (Exonérations & Abattements)", "fieldtype": "Section Break"},
        {"fieldname": "deduct_aapi_exonere", "label": "Quote-part Bénéfice Exonéré AAPI / ANDI (DZD)", "fieldtype": "Currency"},
        {"fieldname": "deduct_nesda_abattement", "label": "Abattement Dégressif NESDA (70%, 50%, 25%) (DZD)", "fieldtype": "Currency"},
        {"fieldname": "deduct_export", "label": "Bénéfice Exportations Exonéré Art. 138-1 (DZD)", "fieldtype": "Currency"},
        {"fieldname": "col_deduct", "fieldtype": "Column Break"},
        {"fieldname": "deduct_sud_50", "label": "Abattement 50% Grand Sud Art. 138 bis (DZD)", "fieldtype": "Currency"},
        {"fieldname": "deduct_deficits_anterieurs", "label": "Déficits Fiscaux Antérieurs Reportables (DZD)", "fieldtype": "Currency"},
        {"fieldname": "total_deductions", "label": "TOTAL DES DÉDUCTIONS (DZD)", "fieldtype": "Currency", "read_only": 1},

        {"fieldname": "sec_result", "label": "3. Détermination du Résultat Fiscal & IBS Net", "fieldtype": "Section Break"},
        {"fieldname": "taxable_fiscal_result", "label": "RÉSULTAT FISCAL IMPOSABLE (DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "ibs_brut", "label": "IBS Brut Calculé (DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "col_res", "fieldtype": "Column Break"},
        {"fieldname": "ibs_net_du", "label": "IBS NET DÉFINITIF DÛ (Min 10 000 DZD)", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "reinvestment_obligation_30", "label": "Obligation Réinvestissement 30% AAPI (DZD)", "fieldtype": "Currency", "read_only": 1}
    ]
    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1})
    doc.insert()
    print("Created DocType: Fiscal Table 9 Engine")
else:
    print("DocType Fiscal Table 9 Engine already exists")

frappe.db.commit()
print("Phase 2 & 3 DocTypes creation complete!")
