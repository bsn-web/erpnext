import frappe

frappe.init(site='frappe.com')
frappe.connect()

dt_name = "Bilan Fiscal"
if frappe.db.exists("DocType", dt_name):
    print("DocType Bilan Fiscal already exists, skipping creation")
else:
    doc = frappe.new_doc("DocType")
    doc.name = dt_name
    doc.module = "Algeria Tax"
    doc.custom = 0
    doc.is_submittable = 1
    doc.track_changes = 1
    doc.autoname = "BF-BSN-.fiscal_year.-.###"

    fields = [
        # --- EN-TÊTE ---
        {"fieldname": "sec_ident", "label": "Identification Administrative & Fiscale", "fieldtype": "Section Break"},
        {"fieldname": "company", "label": "Société", "fieldtype": "Link", "options": "Company", "reqd": 1, "default": "Build And Secure Networks"},
        {"fieldname": "fiscal_year", "label": "Exercice Fiscal", "fieldtype": "Link", "options": "Fiscal Year", "reqd": 1, "default": "2026"},
        {"fieldname": "status", "label": "Statut de la Liasse", "fieldtype": "Select", "options": "Brouillon\nCalculé & Contrôlé\nClôturé & Verrouillé (Lecture Seule)", "default": "Brouillon", "reqd": 1},
        {"fieldname": "col_h1", "fieldtype": "Column Break"},
        {"fieldname": "nif", "label": "N.I.F (15 Chiffres)", "fieldtype": "Data", "default": "001716099938766", "reqd": 1},
        {"fieldname": "company_name_fiscal", "label": "Désignation de l'Entreprise", "fieldtype": "Data", "default": "EURL BUILD AND SECURE NETWORKS"},
        {"fieldname": "activity", "label": "Activité", "fieldtype": "Data", "default": "SERVICE INFORMATIQUE"},
        {"fieldname": "col_h2", "fieldtype": "Column Break"},
        {"fieldname": "address", "label": "Adresse", "fieldtype": "Small Text", "default": "AISSA LALAM N°13 RDC EL MOURADIA -ALGER-"},
        {"fieldname": "period_start_date", "label": "Date Début Exercice", "fieldtype": "Date", "default": "2026-01-01"},
        {"fieldname": "period_end_date", "label": "Date Clôture Exercice", "fieldtype": "Date", "default": "2026-12-31"},
        {"fieldname": "is_locked", "label": "Verrouillé après Clôture", "fieldtype": "Check", "read_only": 1, "default": 0},

        # --- BILAN ACTIF : ACTIFS NON COURANTS ---
        {"fieldname": "sec_actif_non_courant", "label": "BILAN (ACTIF) - Actifs Non Courants", "fieldtype": "Section Break"},
        {"fieldname": "autres_immo_corporelles_brut", "label": "Autres Immo. Corporelles - Brut", "fieldtype": "Currency", "default": "2049257.0"},
        {"fieldname": "autres_immo_corporelles_amort", "label": "Autres Immo. Corporelles - Amort/Prov", "fieldtype": "Currency", "default": "1908344.0"},
        {"fieldname": "autres_immo_corporelles_net", "label": "Autres Immo. Corporelles - Net N", "fieldtype": "Currency", "read_only": 1, "default": "140912.0"},
        {"fieldname": "autres_immo_corporelles_net_n1", "label": "Autres Immo. Corporelles - Net N-1", "fieldtype": "Currency", "default": "140912.0"},
        
        {"fieldname": "col_anc_tot", "fieldtype": "Column Break"},
        {"fieldname": "total_actif_non_courant_brut", "label": "TOTAL ACTIF NON COURANT - Brut", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_non_courant_amort", "label": "TOTAL ACTIF NON COURANT - Amort/Prov", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_non_courant_net", "label": "TOTAL ACTIF NON COURANT - Net N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_non_courant_net_n1", "label": "TOTAL ACTIF NON COURANT - Net N-1", "fieldtype": "Currency"},

        # --- BILAN ACTIF : ACTIFS COURANTS ---
        {"fieldname": "sec_actif_courant", "label": "BILAN (ACTIF) - Actifs Courants & Disponibilités", "fieldtype": "Section Break"},
        {"fieldname": "clients_brut", "label": "Clients - Brut", "fieldtype": "Currency", "default": "11288519.0"},
        {"fieldname": "clients_amort", "label": "Clients - Provisions", "fieldtype": "Currency", "default": "0.0"},
        {"fieldname": "clients_net", "label": "Clients - Net N", "fieldtype": "Currency", "read_only": 1, "default": "11288519.0"},
        {"fieldname": "clients_net_n1", "label": "Clients - Net N-1", "fieldtype": "Currency", "default": "11288519.0"},
        
        {"fieldname": "autres_debiteurs_brut", "label": "Autres Débiteurs - Brut", "fieldtype": "Currency", "default": "414300.0"},
        {"fieldname": "autres_debiteurs_net", "label": "Autres Débiteurs - Net N", "fieldtype": "Currency", "read_only": 1, "default": "414300.0"},
        {"fieldname": "autres_debiteurs_net_n1", "label": "Autres Débiteurs - Net N-1", "fieldtype": "Currency", "default": "414300.0"},

        {"fieldname": "col_ac_1", "fieldtype": "Column Break"},
        {"fieldname": "impots_assimiles_actif_brut", "label": "Impôts et Assimilés (Actif) - Brut", "fieldtype": "Currency", "default": "145385.0"},
        {"fieldname": "impots_assimiles_actif_net", "label": "Impôts et Assimilés - Net N", "fieldtype": "Currency", "read_only": 1, "default": "145385.0"},
        {"fieldname": "impots_assimiles_actif_net_n1", "label": "Impôts et Assimilés - Net N-1", "fieldtype": "Currency", "default": "145385.0"},

        {"fieldname": "tresorerie_actif_brut", "label": "Trésorerie Actif (Banques/Caisse) - Brut", "fieldtype": "Currency", "default": "3941584.0"},
        {"fieldname": "tresorerie_actif_net", "label": "Trésorerie Actif - Net N", "fieldtype": "Currency", "read_only": 1, "default": "3941584.0"},
        {"fieldname": "tresorerie_actif_net_n1", "label": "Trésorerie Actif - Net N-1", "fieldtype": "Currency", "default": "3941584.0"},

        {"fieldname": "col_ac_tot", "fieldtype": "Column Break"},
        {"fieldname": "total_actif_courant_brut", "label": "TOTAL ACTIF COURANT - Brut", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_courant_amort", "label": "TOTAL ACTIF COURANT - Amort/Prov", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_courant_net", "label": "TOTAL ACTIF COURANT - Net N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_actif_courant_net_n1", "label": "TOTAL ACTIF COURANT - Net N-1", "fieldtype": "Currency"},

        # --- BILAN ACTIF : TOTAL GENERAL ---
        {"fieldname": "sec_tot_actif", "label": "TOTAL GÉNÉRAL ACTIF", "fieldtype": "Section Break"},
        {"fieldname": "total_general_actif_brut", "label": "TOTAL GÉNÉRAL ACTIF - Brut", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_general_actif_amort", "label": "TOTAL GÉNÉRAL ACTIF - Amort/Prov", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "col_tot_act", "fieldtype": "Column Break"},
        {"fieldname": "total_general_actif_net", "label": "TOTAL GÉNÉRAL ACTIF - Net N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_general_actif_net_n1", "label": "TOTAL GÉNÉRAL ACTIF - Net N-1", "fieldtype": "Currency"},

        # --- BILAN PASSIF : CAPITAUX PROPRES ---
        {"fieldname": "sec_passif_cp", "label": "BILAN (PASSIF) - Capitaux Propres (Total I)", "fieldtype": "Section Break"},
        {"fieldname": "capital_emis", "label": "Capital Émis", "fieldtype": "Currency", "default": "100000.0"},
        {"fieldname": "capital_emis_n1", "label": "Capital Émis N-1", "fieldtype": "Currency", "default": "100000.0"},
        {"fieldname": "primes_et_reserves", "label": "Primes et Réserves", "fieldtype": "Currency", "default": "10000.0"},
        {"fieldname": "primes_et_reserves_n1", "label": "Primes et Réserves N-1", "fieldtype": "Currency", "default": "10000.0"},

        {"fieldname": "col_cp_1", "fieldtype": "Column Break"},
        {"fieldname": "resultat_net_passif", "label": "Résultat Net de l'Exercice (Passif)", "fieldtype": "Currency", "default": "1399897.0"},
        {"fieldname": "resultat_net_passif_n1", "label": "Résultat Net N-1", "fieldtype": "Currency", "default": "1399897.0"},
        {"fieldname": "report_a_nouveau", "label": "Autres Capitaux Propres - Report à Nouveau", "fieldtype": "Currency", "default": "7301168.0"},
        {"fieldname": "report_a_nouveau_n1", "label": "Report à Nouveau N-1", "fieldtype": "Currency", "default": "7301168.0"},

        {"fieldname": "col_cp_tot", "fieldtype": "Column Break"},
        {"fieldname": "total_capitaux_propres_i", "label": "TOTAL I (Capitaux Propres) N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_capitaux_propres_i_n1", "label": "TOTAL I N-1", "fieldtype": "Currency"},

        # --- BILAN PASSIF : PASSIFS NON COURANTS & COURANTS ---
        {"fieldname": "sec_passif_dettes", "label": "BILAN (PASSIF) - Dettes & Passifs (Total II & III)", "fieldtype": "Section Break"},
        {"fieldname": "emprunts_dettes_financieres", "label": "Emprunts et Dettes Financières (Non Courant)", "fieldtype": "Currency", "default": "296130.0"},
        {"fieldname": "emprunts_dettes_financieres_n1", "label": "Emprunts Financiers N-1", "fieldtype": "Currency", "default": "296130.0"},
        {"fieldname": "total_passifs_non_courants_ii", "label": "TOTAL II (Passifs Non-Courants) N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_passifs_non_courants_ii_n1", "label": "TOTAL II N-1", "fieldtype": "Currency"},

        {"fieldname": "col_p_courant", "fieldtype": "Column Break"},
        {"fieldname": "fournisseurs_comptes_rattaches", "label": "Fournisseurs et Comptes Rattachés", "fieldtype": "Currency", "default": "2490506.0"},
        {"fieldname": "fournisseurs_comptes_rattaches_n1", "label": "Fournisseurs N-1", "fieldtype": "Currency", "default": "2490506.0"},
        {"fieldname": "impots_passif", "label": "Impôts Dus (Passif)", "fieldtype": "Currency", "default": "1730330.0"},
        {"fieldname": "impots_passif_n1", "label": "Impôts Dus N-1", "fieldtype": "Currency", "default": "1730330.0"},

        {"fieldname": "col_p_autres", "fieldtype": "Column Break"},
        {"fieldname": "autres_dettes_passif", "label": "Autres Dettes (Passif)", "fieldtype": "Currency", "default": "2602668.0"},
        {"fieldname": "autres_dettes_passif_n1", "label": "Autres Dettes N-1", "fieldtype": "Currency", "default": "2602668.0"},
        {"fieldname": "total_passifs_courants_iii", "label": "TOTAL III (Passifs Courants) N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_passifs_courants_iii_n1", "label": "TOTAL III N-1", "fieldtype": "Currency"},

        # --- BILAN PASSIF : TOTAL GENERAL & EQUILIBRE ---
        {"fieldname": "sec_tot_passif", "label": "TOTAL GÉNÉRAL PASSIF & CONTRÔLE D'ÉQUILIBRE", "fieldtype": "Section Break"},
        {"fieldname": "total_general_passif", "label": "TOTAL GÉNÉRAL PASSIF (I+II+III) N", "fieldtype": "Currency", "read_only": 1},
        {"fieldname": "total_general_passif_n1", "label": "TOTAL GÉNÉRAL PASSIF N-1", "fieldtype": "Currency"},
        {"fieldname": "col_eq_check", "fieldtype": "Column Break"},
        {"fieldname": "ecart_equilibre_bilan", "label": "Écart Équilibre Bilan (Actif - Passif)", "fieldtype": "Currency", "read_only": 1},

        # --- COMPTE DE RESULTAT (TCR) : PRODUCTION & CONSOMMATIONS ---
        {"fieldname": "sec_tcr_prod_conso", "label": "COMPTE DE RÉSULTAT - Production (I) & Consommations (II)", "fieldtype": "Section Break"},
        {"fieldname": "ventes_marchandises", "label": "Ventes de Marchandises (Crédit)", "fieldtype": "Currency", "default": "10525694.0"},
        {"fieldname": "production_services", "label": "Prestations de Services (Crédit)", "fieldtype": "Currency", "default": "2480000.0"},
        {"fieldname": "chiffre_affaires_net", "label": "Chiffre d'Affaires Net des Rabais", "fieldtype": "Currency", "read_only": 1, "default": "13005694.0"},
        {"fieldname": "total_production_i", "label": "I - PRODUCTION DE L'EXERCICE", "fieldtype": "Currency", "read_only": 1, "default": "13005694.0"},

        {"fieldname": "col_tcr_conso", "fieldtype": "Column Break"},
        {"fieldname": "achats_marchandises", "label": "Achats de Marchandises Vendues (Débit)", "fieldtype": "Currency", "default": "10063349.0"},
        {"fieldname": "autres_consommations", "label": "Autres Consommations (Débit)", "fieldtype": "Currency", "default": "53220.0"},
        {"fieldname": "services_locations", "label": "Services Extérieurs - Locations", "fieldtype": "Currency", "default": "360000.0"},
        {"fieldname": "services_publicite", "label": "Services Extérieurs - Publicité", "fieldtype": "Currency", "default": "30110.0"},
        {"fieldname": "autres_services", "label": "Autres Services Extérieurs", "fieldtype": "Currency", "default": "89010.0"},
        {"fieldname": "total_consommations_ii", "label": "II - CONSOMMATIONS DE L'EXERCICE", "fieldtype": "Currency", "read_only": 1, "default": "10595689.0"},
        {"fieldname": "valeur_ajoutee_iii", "label": "III - VALEUR AJOUTÉE D'EXPLOITATION (I - II)", "fieldtype": "Currency", "read_only": 1, "default": "2410005.0"},

        # --- COMPTE DE RESULTAT (TCR) : EBE, RESULTAT OPERATIONNEL & NET ---
        {"fieldname": "sec_tcr_res", "label": "COMPTE DE RÉSULTAT - EBE (IV), Résultat Opérationnel (V) & Résultat Net (IX)", "fieldtype": "Section Break"},
        {"fieldname": "charges_personnel", "label": "Charges de Personnel", "fieldtype": "Currency", "default": "502527.0"},
        {"fieldname": "impots_taxes_assimiles", "label": "Impôts, Taxes et Versements Assimilés", "fieldtype": "Currency", "default": "98280.0"},
        {"fieldname": "excedent_brut_exploitation_iv", "label": "IV - EXCÉDENT BRUT D'EXPLOITATION (EBE)", "fieldtype": "Currency", "read_only": 1, "default": "1809197.0"},

        {"fieldname": "col_tcr_op", "fieldtype": "Column Break"},
        {"fieldname": "autres_produits_operationnels", "label": "Autres Produits Opérationnels (Crédit)", "fieldtype": "Currency", "default": "95.0"},
        {"fieldname": "autres_charges_operationnelles", "label": "Autres Charges Opérationnelles (Débit)", "fieldtype": "Currency", "default": "2752.0"},
        {"fieldname": "dotations_amortissements", "label": "Dotations aux Amortissements", "fieldtype": "Currency", "default": "396642.0"},
        {"fieldname": "resultat_operationnel_v", "label": "V - RÉSULTAT OPÉRATIONNEL", "fieldtype": "Currency", "read_only": 1, "default": "1409897.0"},

        {"fieldname": "col_tcr_net", "fieldtype": "Column Break"},
        {"fieldname": "resultat_ordinaire_vii", "label": "VII - RÉSULTAT ORDINAIRE (V + VI)", "fieldtype": "Currency", "read_only": 1, "default": "1409897.0"},
        {"fieldname": "impots_exigibles_ibs", "label": "Impôts Exigibles sur Résultats (IBS Dû)", "fieldtype": "Currency", "default": "10000.0"},
        {"fieldname": "resultat_net_exercice_ix", "label": "IX - RÉSULTAT NET DE L'EXERCICE", "fieldtype": "Currency", "read_only": 1, "default": "1399897.0"},

        # --- ANNEXES FISCALES DGI (Tableaux 1 à 13) ---
        {"fieldname": "sec_annexes", "label": "Tableaux Annexes Fiscaux (DGI 1 à 13)", "fieldtype": "Section Break"},
        {"fieldname": "tab1_stocks_neant", "label": "1. Mouvements des Stocks (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab2_production_stockee_neant", "label": "2. Fluctuation Production Stockée (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab3_charges_personnel_neant", "label": "3. Charges Personnel & Impôts Annexes (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab4_charges_produits_operationnels_neant", "label": "4. Autres Charges & Produits Opérationnels (NÉANT)", "fieldtype": "Check", "default": 1},
        
        {"fieldname": "col_tab_5", "fieldtype": "Column Break"},
        {"fieldname": "tab5_dotations_cumulees_debut", "label": "5. Amortissements Corporels Début Exercice", "fieldtype": "Currency", "default": "1908344.0"},
        {"fieldname": "tab5_dotations_cumulees_fin", "label": "5. Amortissements Corporels Fin Exercice", "fieldtype": "Currency", "default": "1908344.0"},
        {"fieldname": "tab6_immo_creees_acquises_neant", "label": "6. Immobilisations Créées/Acquises (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab7_immo_cedees_neant", "label": "7. Immobilisations Cédées (NÉANT)", "fieldtype": "Check", "default": 1},

        {"fieldname": "col_tab_8", "fieldtype": "Column Break"},
        {"fieldname": "tab8_provisions_neant", "label": "8. Provisions & Pertes de Valeur (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab8_1_pertes_creances_neant", "label": "8/1. Relevé Créances Douteuses (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab8_2_pertes_actions_neant", "label": "8/2. Relevé Titres & Filiales (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab9_resultat_fiscal_neant", "label": "9. Tableau Détermination Résultat Fiscal (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab10_affectation_resultat_neant", "label": "10. Affectation Résultat N-1 (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab11_participations_neant", "label": "11. Participations & Filiales (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab12_commissions_honoraires_neant", "label": "12. Commissions & Honoraires (NÉANT)", "fieldtype": "Check", "default": 1},
        {"fieldname": "tab13_tap_neant", "label": "13. Taxe Activité Professionnelle (TAP) (NÉANT)", "fieldtype": "Check", "default": 1}
    ]

    for f in fields:
        doc.append("fields", f)

    doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1})
    doc.append("permissions", {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1, "submit": 1})
    doc.append("permissions", {"role": "Auditor", "read": 1})

    doc.insert()
    frappe.db.commit()
    print("Created DocType: Bilan Fiscal")
