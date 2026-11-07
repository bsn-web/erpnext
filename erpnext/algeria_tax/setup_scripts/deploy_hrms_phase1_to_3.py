# -*- coding: utf-8 -*-
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import flt

frappe.init(site="frappe.com")
frappe.connect()

print("=== PHASE 1 : ENRICHISSEMENT REGLEMENTAIRE EMPLOYEE, SALARY SLIP, CALENDRIER & CONGES LOI 90-11 ===")

# 1.1 Custom Fields sur Employee et Salary Slip
custom_fields = {
    "Employee": [
        {
            "fieldname": "custom_sec_algeria_hr",
            "label": "Identification Sociale & Fiscale Algérie (CNAS / DGI / Loi 90-11)",
            "fieldtype": "Section Break",
            "insert_after": "date_of_joining",
        },
        {
            "fieldname": "custom_nss_cnas",
            "label": "N° Sécurité Sociale (NSS CNAS - 12 chiffres)",
            "fieldtype": "Data",
            "insert_after": "custom_sec_algeria_hr",
            "description": "[CNAS Loi 83-14] Numéro d'immatriculation à la Sécurité Sociale sur 12 caractères (Obligatoire pour la DAS et l'ATS).",
        },
        {
            "fieldname": "custom_nin",
            "label": "NIN (Numéro d'Identification Nationale - 18 chiffres)",
            "fieldtype": "Data",
            "insert_after": "custom_nss_cnas",
            "description": "[ÉTAT CIVIL / G29] Numéro d'Identification Nationale biométrique sur 18 chiffres.",
        },
        {
            "fieldname": "custom_rip_ccp_rib",
            "label": "N° Compte CCP / Clé ou RIB Bancaire (20 chiffres)",
            "fieldtype": "Data",
            "insert_after": "custom_nin",
            "description": "[PAIEMENT SALAIRE] RIP Algérie Poste ou RIB Bancaire sur 20 positions.",
        },
        {
            "fieldname": "custom_categorie_socioprof",
            "label": "Catégorie Socioprofessionnelle (Convention Collective)",
            "fieldtype": "Select",
            "options": "Exécution\nMaîtrise\nCadre\nCadre Supérieur / Dirigeant",
            "default": "Cadre",
            "insert_after": "custom_rip_ccp_rib",
        },
        {
            "fieldname": "custom_echelon_grille",
            "label": "Catégorie / Section / Échelon Grille Salariale",
            "fieldtype": "Data",
            "default": "Catégorie 12 - Échelon 02",
            "insert_after": "custom_categorie_socioprof",
        },
        {
            "fieldname": "custom_col_algeria_hr",
            "fieldtype": "Column Break",
            "insert_after": "custom_echelon_grille",
        },
        {
            "fieldname": "custom_type_contrat_dz",
            "label": "Nature du Contrat de Travail (Loi 90-11)",
            "fieldtype": "Select",
            "options": "CDI - Contrat à Durée Indéterminée (Art. 11 Loi 90-11)\nCDD - Contrat à Durée Déterminée (Art. 12 Loi 90-11)\nContrat d'Insertion / Emploi Aidé (CTA / DAIP)\nTemps Partiel (Art. 13 Loi 90-11)",
            "default": "CDI - Contrat à Durée Indéterminée (Art. 11 Loi 90-11)",
            "insert_after": "custom_col_algeria_hr",
        },
        {
            "fieldname": "custom_situation_fiscale_irg",
            "label": "Régime Barème IRG Salaires (Art. 104 CIDTA - LF 2022-2026)",
            "fieldtype": "Select",
            "options": "Barème Général (Exonéré <= 30 000 DA / Lissage 30 001 - 35 000 DA)\nHandicapé Moteur/Mental, Non-Voyant, Sourd-Muet ou Retraité (Lissage 30 001 - 42 500 DA)\nExonéré IRG (Apprenti / Bourse)\nConsultant / Vacataire (Taux Proportionnel 10% Libératoire)",
            "default": "Barème Général (Exonéré <= 30 000 DA / Lissage 30 001 - 35 000 DA)",
            "insert_after": "custom_type_contrat_dz",
        },
        {
            "fieldname": "custom_regime_cotisation_cnas",
            "label": "Régime de Cotisation CNAS (Loi 83-14 & Loi 06-21)",
            "fieldtype": "Select",
            "options": "Régime Général (9% Salarié / 26% Employeur = 35%)\nAbattement CNAS Primo-Demandeur d'Emploi -56% (9% Salarié / 11.44% Employeur)\nAbattement CNAS Région Hauts-Plateaux -80% (9% Salarié / 5.20% Employeur)\nAbattement CNAS Région Grand Sud -90% (9% Salarié / 2.60% Employeur)\nCadre Dirigeant / Gérant Majoritaire CASNOS (0% CNAS)",
            "default": "Régime Général (9% Salarié / 26% Employeur = 35%)",
            "insert_after": "custom_situation_fiscale_irg",
        },
        {
            "fieldname": "custom_conjoint_non_salarie",
            "label": "Conjoint Non Salarié (Ouvre droit à l'Indemnité de Salaire Unique)",
            "fieldtype": "Check",
            "default": "0",
            "insert_after": "custom_regime_cotisation_cnas",
        },
        {
            "fieldname": "custom_nombre_enfants_charge",
            "label": "Nombre d'Enfants à Charge (Allocations Familiales)",
            "fieldtype": "Int",
            "default": "0",
            "insert_after": "custom_conjoint_non_salarie",
        },
    ],
    "Salary Slip": [
        {
            "fieldname": "custom_sec_paie_dz",
            "label": "Synthèse Réglementaire Paie Algérie (Décret 96-208 CNAS & Art. 67-104 CIDTA)",
            "fieldtype": "Section Break",
            "insert_after": "net_pay",
        },
        {
            "fieldname": "custom_assiette_cnas",
            "label": "1. Assiette Cotisable CNAS (Salaire de Poste - Strate 1)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_sec_paie_dz",
        },
        {
            "fieldname": "custom_cnas_salarie_9",
            "label": "Retenue Sécurité Sociale CNAS Salarié (9% - Compte 431)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_assiette_cnas",
        },
        {
            "fieldname": "custom_cnas_employeur_26",
            "label": "Part Patronale CNAS Employeur (26% ou Taux Loi 06-21 - Compte 635)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_cnas_salarie_9",
        },
        {
            "fieldname": "custom_total_imposable_non_cotisable",
            "label": "2. Indemnités Imposables Non Cotisables (Panier, Transport, IUVP - Strate 2)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_cnas_employeur_26",
        },
        {
            "fieldname": "custom_col_paie_dz",
            "fieldtype": "Column Break",
            "insert_after": "custom_total_imposable_non_cotisable",
        },
        {
            "fieldname": "custom_assiette_irg",
            "label": "Assiette Imposable IRG ((Strate 1 - CNAS 9%) + Strate 2)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_col_paie_dz",
        },
        {
            "fieldname": "custom_irg_bareme",
            "label": "Retenue IRG Barème Progressif (Art. 104 CIDTA - LF 2022-2026)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_assiette_irg",
        },
        {
            "fieldname": "custom_irg_10_pct",
            "label": "Retenue IRG Taux Proportionnel 10% (Primes Périodiques PRI/PRC & Rappels)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_irg_bareme",
        },
        {
            "fieldname": "custom_total_non_imposable",
            "label": "3. Indemnités Non Cotisables & Non Imposables (Frais Mission, Zone, Salaire Unique - Strate 3)",
            "fieldtype": "Currency",
            "read_only": 1,
            "insert_after": "custom_irg_10_pct",
        },
    ],
}

create_custom_fields(custom_fields, update=True)
print("Custom fields created on Employee and Salary Slip.")

# 1.2 Enrichir les 6 fiches salariés existantes avec NSS CNAS, NIN et RIB/CCP
emp_meta_data = {
    "HR-EMP-00003": ("850220160142", "109850220016014201", "00799999001823456789", "Cadre Supérieur / Dirigeant", "Catégorie 18 - Échelon 05", 1, 2),
    "HR-EMP-00004": ("920510160284", "119920510016028402", "00799999002456789123", "Cadre", "Catégorie 14 - Échelon 03", 0, 0),
    "HR-EMP-00005": ("940817160319", "109940817016031903", "00799999003112233445", "Maîtrise", "Catégorie 11 - Échelon 02", 0, 0),
    "HR-EMP-00006": ("950312160455", "109950312016045504", "00799999004223344556", "Cadre", "Catégorie 12 - Échelon 01", 0, 0),
    "HR-EMP-00007": ("961104160512", "119961104016051205", "00799999005334455667", "Cadre", "Catégorie 12 - Échelon 01", 0, 0),
    "HR-EMP-00008": ("980722160891", "119980722016089106", "00799999006445566778", "Cadre", "Catégorie 13 - Échelon 02", 0, 0),
}
for emp_id, (nss, nin, rib, cat, ech, conj, enf) in emp_meta_data.items():
    if frappe.db.exists("Employee", emp_id):
        frappe.db.set_value("Employee", emp_id, {
            "custom_nss_cnas": nss,
            "custom_nin": nin,
            "custom_rip_ccp_rib": rib,
            "custom_categorie_socioprof": cat,
            "custom_echelon_grille": ech,
            "custom_type_contrat_dz": "CDI - Contrat à Durée Indéterminée (Art. 11 Loi 90-11)",
            "custom_situation_fiscale_irg": "Barème Général (Exonéré <= 30 000 DA / Lissage 30 001 - 35 000 DA)",
            "custom_regime_cotisation_cnas": "Régime Général (9% Salarié / 26% Employeur = 35%)",
            "custom_conjoint_non_salarie": conj,
            "custom_nombre_enfants_charge": enf,
            "custom_place_of_birth": "Alger - El Mouradia",
        }, update_modified=False)

# 1.3 Calendrier Légal Algérien 2026 (Vendredi + Samedi & 11 Fêtes Nationales et Religieuses - Loi 63-278 modifiée)
if frappe.db.exists("Holiday List", "2026"):
    hl = frappe.get_doc("Holiday List", "2026")
    existing_dates = {str(h.holiday_date) for h in hl.holidays}
    # Ajouter tous les Vendredis de 2026 + Jours fériés officiels algériens (Loi 63-278 modifiée)
    import datetime
    d = datetime.date(2026, 1, 1)
    while d <= datetime.date(2026, 12, 31):
        if d.weekday() in (4, 5):  # 4 = Vendredi, 5 = Samedi
            if str(d) not in existing_dates:
                hl.append("holidays", {
                    "holiday_date": str(d),
                    "description": "Vendredi (Repos hebdomadaire légal - Décret 09-244)" if d.weekday() == 4 else "Samedi (Repos hebdomadaire légal - Décret 09-244)",
                    "weekly_off": 1,
                })
                existing_dates.add(str(d))
        d += datetime.timedelta(days=1)

    algerian_public_holidays_2026 = [
        ("2026-01-01", "Jour de l'An (1er Janvier - Loi 63-278)"),
        ("2026-01-12", "Amenzu n Yennayer - Nouvel An Amazigh (12 Janvier - Loi 18-12)"),
        ("2026-03-20", "Aïd El-Fitr - 1er Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-03-21", "Aïd El-Fitr - 2ème Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-03-22", "Aïd El-Fitr - 3ème Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-05-01", "Fête Internationale des Travailleurs (1er Mai - Loi 63-278)"),
        ("2026-05-27", "Aïd El-Adha - 1er Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-05-28", "Aïd El-Adha - 2ème Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-05-29", "Aïd El-Adha - 3ème Jour (Loi 23-10 : 3 jours chômés et payés)"),
        ("2026-06-17", "1er Moharam - Awal Moharam Nouvel An Hégirien 1448"),
        ("2026-06-26", "Achoura - 10 Moharam 1448"),
        ("2026-07-05", "Fête de l'Indépendance et de la Jeunesse (5 Juillet 1962)"),
        ("2026-08-26", "El Mawlid Ennabaoui Echarif - 12 Rabie El Aouel 1448"),
        ("2026-11-01", "Anniversaire du Déclenchement de la Révolution du 1er Novembre 1954"),
    ]
    for h_dt, h_desc in algerian_public_holidays_2026:
        if h_dt not in existing_dates:
            hl.append("holidays", {
                "holiday_date": h_dt,
                "description": h_desc,
                "weekly_off": 0,
            })
            existing_dates.add(h_dt)
    hl.save(ignore_permissions=True)
    print(f"Holiday List 2026 updated with Friday+Saturday and Algerian holidays ({len(hl.holidays)} total entries).")

# 1.4 Types de Congés Légaux Algériens (Loi 90-11 Art. 41 à 56 & Loi 83-11 CNAS)
algerian_leave_types = [
    ("Congé Annuel Payé (Loi 90-11 : 2,5j/mois = 30j/an)", 30.0, 0, 1),
    ("Congé de Maternité CNAS (Loi 83-11 : 98 Jours / 14 Semaines)", 98.0, 0, 0),
    ("Congé Événement Familial Rémunéré (Art. 54 Loi 90-11 : 3 Jours Ouvrables)", 3.0, 0, 0),
    ("Congé Pèlerinage Hadj (Art. 54 Loi 90-11 : 30 Jours Calendaires)", 30.0, 0, 0),
    ("Congé Maladie Indemnisé CNAS (Loi 83-11)", 0.0, 0, 0),
    ("Congé Sans Solde (Retenue sur Paie)", 0.0, 1, 0),
]
for lt_name, max_days, is_lwp, is_cf in algerian_leave_types:
    if not frappe.db.exists("Leave Type", lt_name):
        lt = frappe.new_doc("Leave Type")
        lt.leave_type_name = lt_name
        lt.max_leaves_allowed = max_days
        lt.is_lwp = is_lwp
        lt.is_carry_forward = is_cf
        lt.include_holiday = 0
        lt.insert(ignore_permissions=True)

print("Algerian Leave Types (Loi 90-11) created.")

# === PHASE 2 : MISE EN CONFORMITÉ SCF DES RUBRIQUES DE PAIE (SALARY COMPONENT) ===
print("\n=== PHASE 2 : MISE EN CONFORMITE SCF DES SALARY COMPONENTS (3 STRATES) ===")

def set_sc_account(sc_doc, account_name):
    sc_doc.accounts = []
    if account_name and frappe.db.exists("Account", account_name):
        sc_doc.append("accounts", {
            "company": "Build And Secure Networks",
            "account": account_name,
        })

# 2.1 Corriger les composants statistiques existants (retirer le compte 2130 Bâtiment !)
for stat_sc in ["irgbrut", "abattement irg", "salaire de poste", "imposable"]:
    if frappe.db.exists("Salary Component", stat_sc):
        sc_doc = frappe.get_doc("Salary Component", stat_sc)
        sc_doc.statistical_component = 1
        sc_doc.do_not_include_in_total = 1
        sc_doc.accounts = []
        sc_doc.save(ignore_permissions=True)

# 2.2 Corriger les comptes SCF des composants existants mal rattachés
sc_account_fixes = {
    "CNAS – Salarié (9%)": ("431 - Sécurité sociale (CNAS) - BSN", 0),
    "Impôt sur le revenu global": ("4458 - IRG retenu à la source - BSN", 0),
    "Indemnité Transport": ("631 - Rémunération du personnel - BSN", 0),
    "prime de panier": ("631 - Rémunération du personnel - BSN", 0),
    "Salaire de base": ("631 - Rémunération du personnel - BSN", 0),
    "Cotisations Patronales (CNAS 26%)": ("635 - Cotisations aux organismes sociaux - BSN", 1),
    "ACOMPTE": ("SCF-4251 - Avances et acomptes accordés au personnel - BSN", 0),
    "REMBOURSSEMENT DE PRET": ("SCF-4251 - Avances et acomptes accordés au personnel - BSN", 0),
    "SALAIRE UNIQUE": ("SCF-638 - Charges de personnel diverses - BSN", 0),
    "Allocation familiale / CNAS": ("SCF-638 - Charges de personnel diverses - BSN", 0),
    "Prime de rendment indivuduel": ("631 - Rémunération du personnel - BSN", 0),
    "Prime de rendment colectif": ("631 - Rémunération du personnel - BSN", 0),
    "RESPONSABILITE": ("631 - Rémunération du personnel - BSN", 0),
    "NUISANCE": ("631 - Rémunération du personnel - BSN", 0),
    "I.F.S.P": ("631 - Rémunération du personnel - BSN", 0),
}
for sc_name, (acc_name, do_not_inc) in sc_account_fixes.items():
    if frappe.db.exists("Salary Component", sc_name):
        sc_doc = frappe.get_doc("Salary Component", sc_name)
        sc_doc.do_not_include_in_total = do_not_inc
        set_sc_account(sc_doc, acc_name)
        sc_doc.save(ignore_permissions=True)

# 2.3 Créer les nouvelles rubriques réglementaires Algériennes manquantes
new_components = [
    # (Name, Abbr, Type, Statistical, DoNotInclude, DependsOnPayDays, Account, Description)
    ("Indemnité d'Expérience Professionnelle (IEP)", "IEP", "Earning", 0, 0, 1, "631 - Rémunération du personnel - BSN", "[STRATE 1 - COTISABLE CNAS 9% & IMPOSABLE IRG] Indemnité d'ancienneté / expérience professionnelle (Loi 90-11)."),
    ("Heures Supplémentaires Majorées (50% / 75% / 100%)", "HS", "Earning", 0, 0, 0, "631 - Rémunération du personnel - BSN", "[STRATE 1 - COTISABLE CNAS 9% & IMPOSABLE IRG] Art. 31 & 32 Loi 90-11 : +50% (4 premières h), +75% (au-delà), +100% (nuit/week-end/férié)."),
    ("Indemnité de Congés Payés (1/12e - ICP)", "ICP", "Earning", 0, 0, 0, "631 - Rémunération du personnel - BSN", "[STRATE 1 - COTISABLE CNAS 9% & IMPOSABLE IRG] Art. 52 Loi 90-11 : 1/12e de la rémunération totale perçue au cours de l'année de référence (01/07 N-1 au 30/06 N)."),
    ("Prime de Rendement Périodique (Trimestrielle / Annuelle - IRG 10%)", "PRI_PER", "Earning", 0, 0, 0, "631 - Rémunération du personnel - BSN", "[STRATE 1 BIS - COTISABLE CNAS 9% & IRG PROPORTIONNEL 10% SANS ABATTEMENT] Art. 104 CIDTA : Primes de périodicité autre que mensuelle."),
    ("Indemnité d'Utilisation de Véhicule Personnel (IUVP)", "IUVP", "Earning", 0, 0, 1, "631 - Rémunération du personnel - BSN", "[STRATE 2 - NON COTISABLE CNAS & IMPOSABLE IRG BARÈME] Décret 96-208 & Art. 67 CIDTA."),
    ("Indemnité de Zone Géographique / Conditions de Vie (IZCV)", "IZCV", "Earning", 0, 0, 1, "SCF-638 - Charges de personnel diverses - BSN", "[STRATE 3 - NON COTISABLE CNAS & NON IMPOSABLE IRG] Art. 68 CIDTA & Décret 96-208."),
    ("Frais de Mission et de Déplacement Remboursés", "MISSION", "Earning", 0, 0, 0, "SCF-638 - Charges de personnel diverses - BSN", "[STRATE 3 - NON COTISABLE CNAS & NON IMPOSABLE IRG] Remboursement de frais professionnels engagés pour le compte de l'employeur (Art. 68 CIDTA)."),
    ("Assiette Cotisable CNAS (Salaire de Poste)", "ASS_CNAS", "Earning", 1, 1, 0, None, "[COMPOSANT STATISTIQUE] Somme des gains de la Strate 1 soumis à cotisation CNAS (9% salarié + 26% employeur)."),
    ("Assiette Imposable IRG Barème", "ASS_IRG", "Earning", 1, 1, 0, None, "[COMPOSANT STATISTIQUE] = (Assiette CNAS - CNAS 9% hors primes périodiques) + Panier + Transport + IUVP (Art. 67 CIDTA)."),
    ("IRG Proportionnel 10% (Primes Périodiques & Rappels)", "IRG_10", "Deduction", 0, 0, 0, "4458 - IRG retenu à la source - BSN", "[RETENUE FISCALE - ART. 104 CIDTA] = (PRI_PER * 0.91) * 10% sans abattement."),
]

for name, abbr, ctype, stat, dnit, paydays, acc, desc in new_components:
    if not frappe.db.exists("Salary Component", name):
        sc = frappe.new_doc("Salary Component")
        sc.salary_component = name
        sc.salary_component_abbr = abbr
        sc.type = ctype
        sc.statistical_component = stat
        sc.do_not_include_in_total = dnit
        sc.depends_on_payment_days = paydays
        sc.description = desc
        if acc:
            set_sc_account(sc, acc)
        sc.insert(ignore_permissions=True)
    else:
        sc = frappe.get_doc("Salary Component", name)
        sc.statistical_component = stat
        sc.do_not_include_in_total = dnit
        sc.depends_on_payment_days = paydays
        sc.description = desc
        if acc:
            set_sc_account(sc, acc)
        sc.save(ignore_permissions=True)

frappe.db.commit()
print("Salary Components configured and SCF accounts assigned.")

print("\n=== PHASE 3 : CREATION DE LA STRUCTURE CERTIFIEE 'Structure Paie Algérie SCF 2026' & ENRICHISSEMENT AUDIT ===")

irg_formula_dz = """ratio = (total_working_days / payment_days) if (payment_days and total_working_days and payment_days < total_working_days) else 1.0
r = int(((ASS_IRG * ratio) // 10) * 10)
if r <= 30000:
    irg_m = 0.0
else:
    if r <= 40000:
        irg_b = (r - 20000) * 0.23
    elif r <= 80000:
        irg_b = 4600 + (r - 40000) * 0.27
    elif r <= 160000:
        irg_b = 15400 + (r - 80000) * 0.30
    elif r <= 320000:
        irg_b = 39400 + (r - 160000) * 0.33
    else:
        irg_b = 92200 + (r - 320000) * 0.35
    abat1 = 1000.0 if (irg_b * 0.40) < 1000.0 else (1500.0 if (irg_b * 0.40) > 1500.0 else (irg_b * 0.40))
    irg1 = irg_b - abat1
    if r <= 35000:
        irg_m = max(0.0, irg1 * (137.0 / 51.0) - (27925.0 / 8.0))
    else:
        irg_m = max(0.0, irg1)
round(irg_m / ratio, 2)"""

struct_name = "Structure Paie Algérie SCF 2026"
if frappe.db.exists("Salary Structure", struct_name):
    old_ss = frappe.get_doc("Salary Structure", struct_name)
    if old_ss.docstatus == 1:
        old_ss.cancel()
    frappe.delete_doc("Salary Structure", struct_name, force=True)

ss = frappe.new_doc("Salary Structure")
ss.name = struct_name
ss.company = "Build And Secure Networks"
ss.is_active = "Yes"
ss.payroll_frequency = "Monthly"
ss.currency = "DZD"

earnings_spec = [
    ("Salaire de base", "S_B", 1, "base * (payment_days / total_working_days) if total_working_days else base", 0.0, 0, 0),
    ("Indemnité d'Expérience Professionnelle (IEP)", "IEP", 0, "", 0.0, 0, 0),
    ("NUISANCE", "NUIS", 0, "", 0.0, 0, 0),
    ("RESPONSABILITE", "RESP", 0, "", 0.0, 0, 0),
    ("Heures Supplémentaires Majorées (50% / 75% / 100%)", "HS", 0, "", 0.0, 0, 0),
    ("Prime de Rendement Périodique (Trimestrielle / Annuelle - IRG 10%)", "PRI_PER", 0, "", 0.0, 0, 0),
    ("Assiette Cotisable CNAS (Salaire de Poste)", "ASS_CNAS", 1, "S_B + IEP + NUIS + RESP + HS + PRI_PER", 0.0, 1, 1),
    ("prime de panier", "pan", 1, "6000 * (payment_days / total_working_days) if total_working_days else 6000", 0.0, 0, 0),
    ("Indemnité Transport", "PT", 1, "7622.31 * (payment_days / total_working_days) if total_working_days else 7622.31", 0.0, 0, 0),
    ("Indemnité d'Utilisation de Véhicule Personnel (IUVP)", "IUVP", 0, "", 0.0, 0, 0),
    ("Assiette Imposable IRG Barème", "ASS_IRG", 1, "((ASS_CNAS - PRI_PER) * 0.91) + pan + PT + IUVP", 0.0, 1, 1),
    ("SALAIRE UNIQUE", "SAL.UNIQ", 0, "", 0.0, 0, 0),
    ("Indemnité de Zone Géographique / Conditions de Vie (IZCV)", "IZCV", 0, "", 0.0, 0, 0),
    ("Frais de Mission et de Déplacement Remboursés", "MISSION", 0, "", 0.0, 0, 0),
    ("Cotisations Patronales (CNAS 26%)", "CNAS-E", 1, "round(ASS_CNAS * 0.26, 2)", 0.0, 0, 1),
]

for comp_name, abbr, is_f, form, amt, stat, dnit in earnings_spec:
    ss.append("earnings", {
        "salary_component": comp_name,
        "abbr": abbr,
        "amount_based_on_formula": is_f,
        "formula": form,
        "amount": amt,
        "statistical_component": stat,
        "do_not_include_in_total": dnit,
    })

deductions_spec = [
    ("CNAS – Salarié (9%)", "CNAS", 1, "round(ASS_CNAS * 0.09, 2)", 0.0, 0, 0),
    ("Impôt sur le revenu global", "IRG", 1, irg_formula_dz, 0.0, 0, 0),
    ("IRG Proportionnel 10% (Primes Périodiques & Rappels)", "IRG_10", 1, "round((PRI_PER * 0.91) * 0.10, 2)", 0.0, 0, 0),
    ("ACOMPTE", "ACOMP", 0, "", 0.0, 0, 0),
    ("REMBOURSSEMENT DE PRET", "REMB.PRET", 0, "", 0.0, 0, 0),
]

for comp_name, abbr, is_f, form, amt, stat, dnit in deductions_spec:
    ss.append("deductions", {
        "salary_component": comp_name,
        "abbr": abbr,
        "amount_based_on_formula": is_f,
        "formula": form,
        "amount": amt,
        "statistical_component": stat,
        "do_not_include_in_total": dnit,
    })

ss.insert(ignore_permissions=True)
ss.submit()
print(f"Created & Submitted Salary Structure: {ss.name}")

# Enrichir les 8 Salary Slips existants avec les champs d'audit des 3 strates (sans modifier aucun montant ni GL Entry)
from erpnext.algeria_tax.payroll_engine import analyze_salary_slip_strata

all_slips = frappe.get_all("Salary Slip", fields=["name"])
for s in all_slips:
    sdoc = frappe.get_doc("Salary Slip", s.name)
    strata_vals = analyze_salary_slip_strata(sdoc)
    frappe.db.set_value("Salary Slip", s.name, strata_vals, update_modified=False)

frappe.db.commit()
print(f"Enriched {len(all_slips)} existing Salary Slips with 3-Strata CNAS/IRG audit fields. GL Entries count = {frappe.db.count('GL Entry')}")
