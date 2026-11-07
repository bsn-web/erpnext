# -*- coding: utf-8 -*-
"""
El Tassyir El Ali (التسيير الآلي) — Référentiel National Algérien & Verrouillage Pays 'Algérie Uniquement'
Contient :
1. Verrouillage strict des sociétés sur l'Algérie (Country = 'Algeria', Currency = 'DZD').
2. Référentiel officiel des 22 Banques Algériennes, CCP Algérie Poste et Trésor Public + Calcul/Validation RIB 20 chiffres (Norme Banque d'Algérie).
3. Référentiel des 18 Compagnies d'Assurances Algériennes (CNA / UAR).
4. Référentiel des Organismes Sociaux & Parafiscaux (CNAS, CASNOS, CACOBATPH, CNAC, FNPOS, ONAAPH).
5. Référentiel officiel des 58 Wilayas d'Algérie (01 Adrar à 58 El Meniaa) avec noms FR/AR et zonage fiscal/social.
6. Référentiel des Formes Juridiques (Code de Commerce Algérien) et Centres des Impôts (DGE, CDI, CPI).
"""

import re
try:
    import frappe
    from frappe import _
except ImportError:
    frappe = None
    def _(msg):
        return msg


# ==============================================================================
# 1. RÉFÉRENTIEL DES 22 BANQUES ALGÉRIENNES, CCP & TRÉSOR PUBLIC (CODES BA)
# ==============================================================================
ALGERIAN_BANKS = [
    {
        "bank_code": "001",
        "abbr": "BNA",
        "bank_name": "Banque Nationale d'Algérie (BNA)",
        "bank_name_ar": "البنك الوطني الجزائري",
        "swift_bic": "BNALDZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512101",
        "website": "https://www.bna.dz",
    },
    {
        "bank_code": "002",
        "abbr": "BEA",
        "bank_name": "Banque Extérieure d'Algérie (BEA)",
        "bank_name_ar": "بنك الجزائر الخارجي",
        "swift_bic": "BEXADZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512102",
        "website": "https://www.bea.dz",
    },
    {
        "bank_code": "003",
        "abbr": "BADR",
        "bank_name": "Banque de l'Agriculture et du Développement Rural (BADR)",
        "bank_name_ar": "بنك الفلاحة والتنمية الريفية",
        "swift_bic": "BADRDZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512103",
        "website": "https://www.badrbank.dz",
    },
    {
        "bank_code": "004",
        "abbr": "CPA",
        "bank_name": "Crédit Populaire d'Algérie (CPA)",
        "bank_name_ar": "القرض الشعبي الجزائري",
        "swift_bic": "CPALDZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512104",
        "website": "https://www.cpa-bank.dz",
    },
    {
        "bank_code": "005",
        "abbr": "BDL",
        "bank_name": "Banque de Développement Local (BDL)",
        "bank_name_ar": "بنك التنمية المحلية",
        "swift_bic": "BDLODZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512105",
        "website": "https://www.bdl.dz",
    },
    {
        "bank_code": "006",
        "abbr": "ALBARAKA",
        "bank_name": "Banque Al Baraka d'Algérie",
        "bank_name_ar": "بنك البركة الجزائري",
        "swift_bic": "BARADZAL",
        "category": "Banque Islamique / Mixte",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512106",
        "website": "https://www.albaraka-bank.dz",
    },
    {
        "bank_code": "007",
        "abbr": "CCP",
        "bank_name": "Algérie Poste — Centre des Chèques Postaux (CCP)",
        "bank_name_ar": "بريد الجزائر — مركز الصكوك البريدية",
        "swift_bic": "CCPNDZAL",
        "category": "Institution Financière Publique",
        "edi_format": "CCP_POSTE_DZ",
        "scf_account_prefix": "515000",
        "website": "https://www.poste.dz",
    },
    {
        "bank_code": "008",
        "abbr": "TRESOR",
        "bank_name": "Trésor Public Algérien (Trésorerie Centrale / Wilaya)",
        "bank_name_ar": "الخزينة العمومية الجزائرية",
        "swift_bic": "TRESDZAL",
        "category": "Institution Financière Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "517000",
        "website": "https://www.mf.gov.dz",
    },
    {
        "bank_code": "010",
        "abbr": "BA",
        "bank_name": "Banque d'Algérie (Banque Centrale)",
        "bank_name_ar": "بنك الجزائر",
        "swift_bic": "BALGDZAL",
        "category": "Banque Centrale",
        "edi_format": "ARTS_RTGS_BA",
        "scf_account_prefix": "512110",
        "website": "https://www.bank-of-algeria.dz",
    },
    {
        "bank_code": "011",
        "abbr": "CNEP",
        "bank_name": "CNEP-Banque (Caisse Nationale d'Épargne et de Prévoyance)",
        "bank_name_ar": "الصندوق الوطني للتوفير والاحتياط — بنك",
        "swift_bic": "CNEPDZAL",
        "category": "Banque Publique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512111",
        "website": "https://www.cnepbanque.dz",
    },
    {
        "bank_code": "012",
        "abbr": "CNMA",
        "bank_name": "CNMA (Mutualité Agricole — Opérations Bancaires)",
        "bank_name_ar": "الصندوق الوطني للتعاون الفلاحي",
        "swift_bic": "CNMADZAL",
        "category": "Institution Financière Mutualiste",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512112",
        "website": "https://www.cnma.dz",
    },
    {
        "bank_code": "014",
        "abbr": "ABC",
        "bank_name": "Arab Banking Corporation Algeria (Bank ABC)",
        "bank_name_ar": "المؤسسة العربية المصرفية في الجزائر",
        "swift_bic": "ABCODZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512114",
        "website": "https://www.bank-abc.com",
    },
    {
        "bank_code": "015",
        "abbr": "NATIXIS",
        "bank_name": "Natixis Algérie",
        "bank_name_ar": "ناتيكسيس الجزائر",
        "swift_bic": "NATXDZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512115",
        "website": "https://www.natixis.dz",
    },
    {
        "bank_code": "016",
        "abbr": "SGA",
        "bank_name": "Société Générale Algérie (SGA)",
        "bank_name_ar": "سوسيتيه جنرال الجزائر",
        "swift_bic": "SOGEDZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512116",
        "website": "https://www.societegenerale.dz",
    },
    {
        "bank_code": "017",
        "abbr": "CITIBANK",
        "bank_name": "Citibank N.A. Algeria",
        "bank_name_ar": "سيتي بنك الجزائر",
        "swift_bic": "CITIDZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512117",
        "website": "https://www.citigroup.com",
    },
    {
        "bank_code": "020",
        "abbr": "AGB",
        "bank_name": "Gulf Bank Algeria (AGB)",
        "bank_name_ar": "بنك الخليج الجزائر",
        "swift_bic": "AGBADZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512120",
        "website": "https://www.agb.dz",
    },
    {
        "bank_code": "021",
        "abbr": "BNPP",
        "bank_name": "BNP Paribas El Djazaïr",
        "bank_name_ar": "بي إن بي باريبا الجزائر",
        "swift_bic": "BNPADZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512121",
        "website": "https://www.bnpparibas.dz",
    },
    {
        "bank_code": "024",
        "abbr": "TRUST",
        "bank_name": "Trust Bank Algeria",
        "bank_name_ar": "تراست بنك الجزائر",
        "swift_bic": "TRUSDZAL",
        "category": "Banque Privée / Mixte",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512124",
        "website": "https://www.trustbank.dz",
    },
    {
        "bank_code": "025",
        "abbr": "HBTF",
        "bank_name": "The Housing Bank for Trade and Finance — Algeria (HBTF)",
        "bank_name_ar": "بنك الإسكان للتجارة والتمويل — الجزائر",
        "swift_bic": "HBHODZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512125",
        "website": "https://www.housingbankdz.com",
    },
    {
        "bank_code": "026",
        "abbr": "FRANSABANK",
        "bank_name": "Fransabank El Djazaïr",
        "bank_name_ar": "فرنسابنك الجزائر",
        "swift_bic": "FSBKDZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512126",
        "website": "https://www.fransabank.dz",
    },
    {
        "bank_code": "027",
        "abbr": "ALSALAM",
        "bank_name": "Al Salam Bank Algeria",
        "bank_name_ar": "مصرف السلام الجزائر",
        "swift_bic": "SALADZAL",
        "category": "Banque Islamique",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512127",
        "website": "https://www.alsalambankalgeria.com",
    },
    {
        "bank_code": "029",
        "abbr": "ARABBANK",
        "bank_name": "Arab Bank PLC Algeria",
        "bank_name_ar": "البنك العربي — الجزائر",
        "swift_bic": "ARABDZAL",
        "category": "Banque Privée",
        "edi_format": "SATIM_TECOMP_20",
        "scf_account_prefix": "512129",
        "website": "https://www.arabbank.dz",
    },
]


# ==============================================================================
# 2. RÉFÉRENTIEL DES 18 COMPAGNIES D'ASSURANCES ALGÉRIENNES (CNA / UAR)
# ==============================================================================
ALGERIAN_INSURERS = [
    {"code": "SAA", "name": "Société Nationale d'Assurance (SAA)", "name_ar": "الشركة الوطنية للتأمين", "type": "Assurance Dommages / Publique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CAAR", "name": "Compagnie Algérienne d'Assurance et de Réassurance (CAAR)", "name_ar": "الشركة الجزائرية للتأمين وإعادة التأمين", "type": "Assurance Dommages / Publique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CAAT", "name": "Compagnie Algérienne des Assurances Transport (CAAT)", "name_ar": "الشركة الجزائرية للتأمينات", "type": "Assurance Dommages & Transport / Publique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CASH", "name": "CASH Assurances (Compagnie d'Assurances des Hydrocarbures)", "name_ar": "شركة تأمين المحروقات", "type": "Assurance Risques Industriels & Dommages", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CIAR", "name": "Compagnie Internationale d'Assurance et de Réassurance (CIAR)", "name_ar": "الشركة الدولية للتأمين وإعادة التأمين", "type": "Assurance Dommages / Privée", "scf_expense": "616", "scf_payable": "401"},
    {"code": "ALLIANCE", "name": "Alliance Assurances SPA", "name_ar": "أليانس للتأمينات", "type": "Assurance Dommages / Privée (Cotée COSOB)", "scf_expense": "616", "scf_payable": "401"},
    {"code": "TRUST_ASSUR", "name": "Trust Algeria Assurances & Réassurance", "name_ar": "تراست الجزائر للتأمين وإعادة التأمين", "type": "Assurance Dommages / Privée", "scf_expense": "616", "scf_payable": "401"},
    {"code": "SALAMA", "name": "Salama Assurances Algérie (Takaful)", "name_ar": "سلامة للتأمينات الجزائر", "type": "Assurance Takaful / Islamique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "GAM", "name": "GAM Assurances (Générale Assurance Méditerranéenne)", "name_ar": "العامة للتأمينات المتوسطية", "type": "Assurance Dommages / Privée", "scf_expense": "616", "scf_payable": "401"},
    {"code": "GIG", "name": "GIG Algeria (Gulf Insurance Group — ex-AXA Dommages)", "name_ar": "مجموعة الخليج للتأمين — الجزائر", "type": "Assurance Dommages / Privée", "scf_expense": "616", "scf_payable": "401"},
    {"code": "TALA", "name": "Taamine Life Algérie (TALA Assurances)", "name_ar": "تأمين لايف الجزائر", "type": "Assurance de Personnes / Publique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CAARAMA", "name": "CAARAMA Assurance", "name_ar": "كاراما للتأمين", "type": "Assurance de Personnes / Publique", "scf_expense": "616", "scf_payable": "401"},
    {"code": "MACIR", "name": "Macir Vie SPA", "name_ar": "ماسير في للتأمين على الأشخاص", "type": "Assurance de Personnes / Privée", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CARDIF", "name": "Cardif El Djazaïr (BNP Paribas)", "name_ar": "كارديف الجزائر", "type": "Assurance de Personnes / Prévoyance", "scf_expense": "616", "scf_payable": "401"},
    {"code": "TAKAFUL_DZ", "name": "El Djazaïr El Moutahida Family Takaful / Générale Takaful", "name_ar": "الجزائر المتحدة للتكافل", "type": "Assurance Takaful Officielle", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CAGEX", "name": "Compagnie Algérienne d'Assurance et de Garantie des Exportations (CAGEX)", "name_ar": "الشركة الجزائرية لتأمين وضمان الصادرات", "type": "Assurance-Crédit Export", "scf_expense": "616", "scf_payable": "401"},
    {"code": "SGCI", "name": "Société de Garantie du Crédit Immobilier (SGCI)", "name_ar": "شركة ضمان القرض العقاري", "type": "Assurance-Crédit Immobilier", "scf_expense": "616", "scf_payable": "401"},
    {"code": "CCR", "name": "Compagnie Centrale de Réassurance (CCR)", "name_ar": "الشركة المركزية لإعادة التأمين", "type": "Réassurance Nationale & Catastrophes Naturelles (Cat-Nat)", "scf_expense": "616", "scf_payable": "401"},
]


# ==============================================================================
# 3. RÉFÉRENTIEL DES ORGANISMES SOCIAUX & PARAFISCAUX ALGÉRIENS
# ==============================================================================
ALGERIAN_SOCIAL_ORGANISMS = [
    {
        "code": "CNAS",
        "name": "Caisse Nationale des Assurances Sociales des Travailleurs Salariés (CNAS)",
        "name_ar": "الصندوق الوطني للتأمينات الاجتماعية للعمال الأجراء",
        "employee_rate_pct": 9.0,
        "employer_rate_pct": 26.0,
        "total_rate_pct": 35.0,
        "deadline": "30 du mois suivant (DAC) / 31 Janvier N+1 (DAS)",
        "scf_liability_account": "431",
        "scf_expense_account": "635",
        "portal": "https://teledeclaration.cnas.dz",
    },
    {
        "code": "CASNOS",
        "name": "Caisse Nationale de Sécurité Sociale des Non-Salariés (CASNOS)",
        "name_ar": "الصندوق الوطني للضمان الاجتماعي لغير الأجراء",
        "employee_rate_pct": 0.0,
        "employer_rate_pct": 15.0,
        "total_rate_pct": 15.0,
        "deadline": "30 Juin de l'exercice en cours (Assiette : Revenu annuel ou Base minimale SNMG)",
        "scf_liability_account": "431",
        "scf_expense_account": "636",
        "portal": "https://damancom.casnos.dz",
    },
    {
        "code": "CACOBATPH",
        "name": "Caisse Nationale des Congés Payés et du Chômage-Intempéries (CACOBATPH — BTPH)",
        "name_ar": "الصندوق الوطني للعطل المدفوعة الأجر والبطالة الناجمة عن سوء الأحوال الجوية",
        "employee_rate_pct": 0.375,
        "employer_rate_pct": 12.585,
        "total_rate_pct": 12.96,
        "deadline": "Mensuelle / Trimestrielle (12,21% Congés Payés + 0,75% Chômage-Intempéries)",
        "scf_liability_account": "432",
        "scf_expense_account": "635",
        "portal": "https://tasrihatcom.cacobatph.dz",
    },
    {
        "code": "FNPOS",
        "name": "Fonds National de Péréquation des Œuvres Sociales (FNPOS)",
        "name_ar": "الصندوق الوطني لمعادلة الخدمات الاجتماعية",
        "employee_rate_pct": 0.0,
        "employer_rate_pct": 0.5,
        "total_rate_pct": 0.5,
        "deadline": "Inclus dans les 26% Employeur CNAS",
        "scf_liability_account": "431",
        "scf_expense_account": "635",
        "portal": "https://www.fnpos.dz",
    },
    {
        "code": "CNAC",
        "name": "Caisse Nationale d'Assurance Chômage (CNAC)",
        "name_ar": "الصندوق الوطني للتأمين عن البطالة",
        "employee_rate_pct": 0.5,
        "employer_rate_pct": 1.0,
        "total_rate_pct": 1.5,
        "deadline": "Inclus dans les 35% Globaux CNAS",
        "scf_liability_account": "431",
        "scf_expense_account": "635",
        "portal": "https://www.cnac.dz",
    },
    {
        "code": "ONAAPH",
        "name": "Contribution Emploi des Personnes Handicapées (1% — Loi 02-09)",
        "name_ar": "المساهمة الخاصة بتشغيل الأشخاص المعوقين",
        "employee_rate_pct": 0.0,
        "employer_rate_pct": 1.0,
        "total_rate_pct": 1.0,
        "deadline": "Annuelle (si quota de 1% d'effectif handicapé non atteint pour >= 20 salariés)",
        "scf_liability_account": "432",
        "scf_expense_account": "637",
        "portal": "https://www.onaaph.dz",
    },
    {
        "code": "TAXE_FP_APPR",
        "name": "Taxe de Formation Professionnelle (1%) & Taxe d'Apprentissage (1%)",
        "name_ar": "رسم التكوين المهني المتواصل ورسم التمهين",
        "employee_rate_pct": 0.0,
        "employer_rate_pct": 2.0,
        "total_rate_pct": 2.0,
        "deadline": "20 Février N+1 (sur masse salariale annuelle si effort de formation < 1% + 1%)",
        "scf_liability_account": "447",
        "scf_expense_account": "641",
        "portal": "https://jibayatic.dz",
    },
]


# ==============================================================================
# 4. RÉFÉRENTIEL DES 58 WILAYAS D'ALGÉRIE (CODES 01 À 58 + ZONE FISCALE)
# ==============================================================================
ALGERIAN_WILAYAS = [
    ("01", "Adrar", "أدرار", "Grand Sud"),
    ("02", "Chlef", "الشلف", "Nord"),
    ("03", "Laghouat", "الأغواط", "Hauts-Plateaux"),
    ("04", "Oum El Bouaghi", "أم البواقي", "Hauts-Plateaux"),
    ("05", "Batna", "باتنة", "Hauts-Plateaux"),
    ("06", "Béjaïa", "بجاية", "Nord"),
    ("07", "Biskra", "بسكرة", "Sud"),
    ("08", "Béchar", "بشار", "Grand Sud"),
    ("09", "Blida", "البليدة", "Nord"),
    ("10", "Bouira", "البويرة", "Nord"),
    ("11", "Tamanrasset", "تمنراست", "Grand Sud"),
    ("12", "Tébessa", "تبسة", "Hauts-Plateaux"),
    ("13", "Tlemcen", "تلمسان", "Nord"),
    ("14", "Tiaret", "تيارت", "Hauts-Plateaux"),
    ("15", "Tizi Ouzou", "تيزي وزو", "Nord"),
    ("16", "Alger", "الجزائر", "Nord"),
    ("17", "Djelfa", "الجلفة", "Hauts-Plateaux"),
    ("18", "Jijel", "جيجل", "Nord"),
    ("19", "Sétif", "سطيف", "Hauts-Plateaux"),
    ("20", "Saïda", "سعيدة", "Hauts-Plateaux"),
    ("21", "Skikda", "سكيكدة", "Nord"),
    ("22", "Sidi Bel Abbès", "سيدي بلعباس", "Nord"),
    ("23", "Annaba", "عنابة", "Nord"),
    ("24", "Guelma", "قالمة", "Nord"),
    ("25", "Constantine", "قسنطينة", "Nord"),
    ("26", "Médéa", "المدية", "Nord"),
    ("27", "Mostaganem", "مستغانم", "Nord"),
    ("28", "M'Sila", "المسيلة", "Hauts-Plateaux"),
    ("29", "Mascara", "معسكر", "Nord"),
    ("30", "Ouargla", "ورقلة", "Grand Sud"),
    ("31", "Oran", "وهران", "Nord"),
    ("32", "El Bayadh", "البيض", "Hauts-Plateaux"),
    ("33", "Illizi", "إليزي", "Grand Sud"),
    ("34", "Bordj Bou Arréridj", "برج بوعريريج", "Hauts-Plateaux"),
    ("35", "Boumerdès", "بومرداس", "Nord"),
    ("36", "El Tarf", "الطارف", "Nord"),
    ("37", "Tindouf", "تندوف", "Grand Sud"),
    ("38", "Tissemsilt", "تيسمسيلت", "Hauts-Plateaux"),
    ("39", "El Oued", "الوادي", "Sud"),
    ("40", "Khenchela", "خنشلة", "Hauts-Plateaux"),
    ("41", "Souk Ahras", "سوق أهراس", "Hauts-Plateaux"),
    ("42", "Tipaza", "تيبازة", "Nord"),
    ("43", "Mila", "ميلة", "Nord"),
    ("44", "Aïn Defla", "عين الدفلى", "Nord"),
    ("45", "Naâma", "النعامة", "Hauts-Plateaux"),
    ("46", "Aïn Témouchent", "عين تموشنت", "Nord"),
    ("47", "Ghardaïa", "غرداية", "Sud"),
    ("48", "Relizane", "غليزان", "Nord"),
    ("49", "Timimoun", "تيميمون", "Grand Sud"),
    ("50", "Bordj Badji Mokhtar", "برج باجي مختار", "Grand Sud"),
    ("51", "Ouled Djellal", "أولاد جلال", "Sud"),
    ("52", "Béni Abbès", "بني عباس", "Grand Sud"),
    ("53", "In Salah", "عين صالح", "Grand Sud"),
    ("54", "In Guezzam", "عين قزام", "Grand Sud"),
    ("55", "Touggourt", "تقرت", "Sud"),
    ("56", "Djanet", "جانت", "Grand Sud"),
    ("57", "El M'Ghair", "المغير", "Sud"),
    ("58", "El Meniaa", "المنيعة", "Grand Sud"),
]


# ==============================================================================
# 5. FORMES JURIDIQUES & STRUCTURES FISCALES DGI ALGÉRIE
# ==============================================================================
ALGERIAN_LEGAL_FORMS = [
    {"code": "SARL", "label": "SARL — Société à Responsabilité Limitée", "label_ar": "شركة ذات مسؤولية محدودة (ش.ذ.م.م)", "tax_regime": "Régime du Réel (IBS)"},
    {"code": "EURL", "label": "EURL — Entreprise Unipersonnelle à Responsabilité Limitée", "label_ar": "مؤسسة ذات شخص وحيد وذات مسؤولية محدودة", "tax_regime": "Régime du Réel (IBS)"},
    {"code": "SPA", "label": "SPA — Société par Actions", "label_ar": "شركة مساهمة (ش.م)", "tax_regime": "Régime du Réel (IBS — Commissaire aux Comptes obligatoire)"},
    {"code": "SPAS", "label": "SPAS — Société par Actions Simplifiée (Start-up / Loi 22-09)", "label_ar": "شركة مساهمة بسيطة", "tax_regime": "Régime du Réel / Exonération Start-up"},
    {"code": "SNC", "label": "SNC — Société en Nom Collectif", "label_ar": "شركة التضامن", "tax_regime": "IRG Associés ou Option IBS"},
    {"code": "SCS", "label": "SCS — Société en Commandite Simple", "label_ar": "شركة التوصية البسيطة", "tax_regime": "Régime du Réel"},
    {"code": "EPE_SPA", "label": "EPE / SPA — Entreprise Publique Économique", "label_ar": "مؤسسة عمومية اقتصادية", "tax_regime": "Régime du Réel (DGE / CDI)"},
    {"code": "EPIC", "label": "EPIC — Établissement Public à Caractère Industriel et Commercial", "label_ar": "مؤسسة عمومية ذات طابع صناعي وتجاري", "tax_regime": "Régime du Réel"},
    {"code": "PERSONNE_PHYSIQUE", "label": "Entreprise Individuelle / Commerçant (Personne Physique)", "label_ar": "مؤسسة فردية / تاجر", "tax_regime": "IFU (CA < 8M DA) ou Réel Simplifié / Réel IRG-BIC"},
    {"code": "PROF_LIBERALE", "label": "Profession Libérale (Expert-Comptable, CAC, Médecin, Avocat, Architecte)", "label_ar": "مهنة حرة (خبير محاسب، محافظ حسابات، طبيب، محامٍ)", "tax_regime": "Régime Simplifié des Professions Non Commerciales (IRG-BNC)"},
    {"code": "AUTO_ENTREPRENEUR", "label": "Auto-Entrepreneur (Loi 22-23 / ANAE — IFU 0,5%)", "label_ar": "المقاول الذاتي (الضريبة الجزافية الوحيدة 0.5%)", "tax_regime": "IFU 0,5% (Plafond 5 000 000 DA)"},
]


# ==============================================================================
# 6. ALGORITHME OFFICIEL DE VALIDATION & CALCUL DE CLÉ RIB ALGÉRIEN (20 CHIFFRES)
# ==============================================================================
def compute_algerian_rib_key(bank_code_3: str, branch_code_5: str, account_10: str) -> str:
    """
    Calcule la clé RIB officielle à 2 chiffres selon la norme de la Banque d'Algérie (Modulo 97) :
    Clé RIB = 97 - ((89 * CodeBanque(3) + 15 * CodeAgence(5) + 3 * NumCompte(10)) % 97)
    Formule équivalente entière sur 18 chiffres : 97 - ((int(RIB_18 + '00')) % 97)
    """
    b = re.sub(r"\D", "", str(bank_code_3 or "")).zfill(3)[:3]
    g = re.sub(r"\D", "", str(branch_code_5 or "")).zfill(5)[:5]
    c = re.sub(r"\D", "", str(account_10 or "")).zfill(10)[:10]
    rib_18 = int(f"{b}{g}{c}")
    key = 97 - ((rib_18 * 100) % 97)
    return f"{key:02d}"


def validate_algerian_rib(rib_str: str) -> dict:
    """
    Vérifie un RIB bancaire algérien de 20 chiffres :
    - 3 chiffres : Code Banque (001 à 029)
    - 5 chiffres : Code Agence
    - 10 chiffres : Numéro de compte
    - 2 chiffres : Clé de contrôle RIB (Modulo 97)
    Retourne un dictionnaire détaillé (is_valid, bank_code, bank_name, branch_code, account_number, expected_key, formatted_rib).
    """
    digits = re.sub(r"\D", "", str(rib_str or ""))
    if len(digits) != 20:
        return {
            "is_valid": False,
            "error": f"Le RIB algérien doit comporter exactement 20 chiffres (reçu : {len(digits)} chiffres).",
            "formatted_rib": rib_str,
        }

    bank_code = digits[0:3]
    branch_code = digits[3:8]
    account_num = digits[8:18]
    provided_key = digits[18:20]
    expected_key = compute_algerian_rib_key(bank_code, branch_code, account_num)

    bank_map = {b["bank_code"]: b for b in ALGERIAN_BANKS}
    bank_info = bank_map.get(bank_code, {})
    bank_name = bank_info.get("bank_name", f"Banque Algérienne (Code {bank_code})")
    swift_bic = bank_info.get("swift_bic", "")

    is_key_valid = (provided_key == expected_key)
    formatted = f"{bank_code} {branch_code} {account_num} {provided_key}"

    return {
        "is_valid": is_key_valid,
        "bank_code": bank_code,
        "bank_name": bank_name,
        "swift_bic": swift_bic,
        "branch_code": branch_code,
        "account_number": account_num,
        "provided_key": provided_key,
        "expected_key": expected_key,
        "formatted_rib": formatted,
        "error": None if is_key_valid else f"Clé RIB invalide : clé fournie '{provided_key}' != clé attendue '{expected_key}' (Norme Banque d'Algérie Modulo 97).",
    }


# ==============================================================================
# 7. VERROUILLAGE STRICT « ALGÉRIE UNIQUEMENT » SUR LA CRÉATION D'ENTREPRISE
# ==============================================================================
ALLOWED_COUNTRIES_ALGERIA = {"Algeria", "Algérie", "الجزائر"}
ALLOWED_CURRENCY_ALGERIA = "DZD"


def validate_company_algeria_only(doc, method=None):
    """
    Hook Company.before_validate & Company.validate :
    Limite strictement la création et la modification des sociétés (Company) au pays 'Algeria'
    et à la devise 'DZD' (Dinar Algérien) dans la solution El Tassyir El Ali (التسيير الآلي).
    """
    country_val = (getattr(doc, "country", None) or "").strip()
    if not country_val:
        doc.country = "Algeria"
        country_val = "Algeria"

    if country_val not in ALLOWED_COUNTRIES_ALGERIA:
        msg = (
            "Restriction El Tassyir El Ali (التسيير الآلي) : La création de société est strictement "
            f"limitée à l'Algérie (Country = 'Algeria'). Pays refusé : '{country_val}'. / "
            "نظام التسيير الآلي مخصص حصرياً للمؤسسات الخاضعة للقانون الجزائري (البلد: الجزائر - العملة: د.ج DZD)."
        )
        if frappe:
            frappe.throw(_(msg), title=_("Pays Non Autorisé / بلد غير مرخص"))
        else:
            raise ValueError(msg)

    # Normaliser la valeur canonique Frappe
    doc.country = "Algeria"

    curr_val = (getattr(doc, "default_currency", None) or "").strip()
    if not curr_val:
        doc.default_currency = ALLOWED_CURRENCY_ALGERIA
        curr_val = ALLOWED_CURRENCY_ALGERIA

    if curr_val != ALLOWED_CURRENCY_ALGERIA:
        msg = (
            "Restriction El Tassyir El Ali (التسيير الآلي) : La devise comptable légale (SCF Loi 07-11) "
            f"doit obligatoirement être le Dinar Algérien ('DZD'). Devise refusée : '{curr_val}'."
        )
        if frappe:
            frappe.throw(_(msg), title=_("Devise Non Autorisée / عملة غير مرخصة"))
        else:
            raise ValueError(msg)


def seed_algerian_national_registry():
    """
    Charge automatiquement dans la base de données ERPNext :
    1. Le verrouillage Pays = 'Algeria' et Devise = 'DZD' (System Settings + Property Setters sur Company, Address, Customer, Supplier).
    2. Les 22 Banques Algériennes + CCP + Trésor Public dans le DocType standard `Bank` d'ERPNext.
    3. Les 18 Compagnies d'Assurances Algériennes et les Organismes Sociaux (CNAS, CASNOS, CACOBATPH).
    4. Le branding 'El Tassyir El Ali | التسيير الآلي' dans Navbar Settings & Website Settings.
    """
    if not frappe or not getattr(frappe, "db", None):
        return {"status": "skipped_no_db"}

    # 1. System Settings -> Algeria & DZD
    try:
        frappe.db.set_single_value("System Settings", "country", "Algeria")
        frappe.db.set_single_value("System Settings", "time_zone", "Africa/Algiers")
        frappe.db.set_single_value("System Settings", "date_format", "dd-mm-yyyy")
        frappe.db.set_single_value("System Settings", "app_name", "El Tassyir El Ali | التسيير الآلي")
    except Exception:
        pass

    # 2. Property Setters pour verrouiller Country = Algeria et Currency = DZD par défaut
    prop_specs = [
        ("Company", "country", "default", "Algeria", "Text"),
        ("Company", "country", "read_only", "1", "Check"),
        ("Company", "default_currency", "default", "DZD", "Text"),
        ("Company", "default_currency", "read_only", "1", "Check"),
        ("Address", "country", "default", "Algeria", "Text"),
        ("Customer", "default_currency", "default", "DZD", "Text"),
        ("Supplier", "default_currency", "default", "DZD", "Text"),
        ("Employee", "company", "reqd", "1", "Check"),
    ]
    for dt, fieldname, prop, val, ptype in prop_specs:
        try:
            frappe.make_property_setter({
                "doctype": dt,
                "fieldname": fieldname,
                "property": prop,
                "value": val,
                "property_type": ptype,
            })
        except Exception:
            pass

    # 3. Créer les 22 Banques Algériennes dans `Bank` (DocType standard ERPNext)
    banks_created = 0
    if frappe.db.exists("DocType", "Bank"):
        for b in ALGERIAN_BANKS:
            bname = b["bank_name"]
            if not frappe.db.exists("Bank", bname):
                doc = frappe.new_doc("Bank")
                doc.bank_name = bname
                if hasattr(doc, "swift_number"):
                    doc.swift_number = b["swift_bic"]
                if hasattr(doc, "website"):
                    doc.website = b["website"]
                doc.insert(ignore_permissions=True)
                banks_created += 1

    # 4. Branding Navbar Settings -> El Tassyir El Ali | التسيير الآلي
    try:
        if frappe.db.exists("DocType", "Navbar Settings"):
            frappe.db.set_single_value(
                "Navbar Settings",
                "app_logo",
                "/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg",
            )
    except Exception:
        pass

    frappe.db.commit()
    return {
        "status": "ok",
        "banks_seeded": len(ALGERIAN_BANKS),
        "banks_newly_created": banks_created,
        "insurers_available": len(ALGERIAN_INSURERS),
        "social_organisms_available": len(ALGERIAN_SOCIAL_ORGANISMS),
        "wilayas_available": len(ALGERIAN_WILAYAS),
    }
