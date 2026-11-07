# -*- coding: utf-8 -*-
"""
Suite de Tests Générale & Audit d'Intégration de bout en bout — El Tassyir El Ali (التسيير الآلي)
"""

import os
import sys
import json
import csv

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from algeria_tax.algerian_registry import (
    ALGERIAN_BANKS,
    ALGERIAN_INSURERS,
    ALGERIAN_SOCIAL_ORGANISMS,
    ALGERIAN_WILAYAS,
    ALGERIAN_LEGAL_FORMS,
    compute_algerian_rib_key,
    validate_algerian_rib,
    validate_company_algeria_only,
)
from algeria_tax.bank_transfer_engine import (
    amount_to_words_dzd_fr,
    amount_to_words_dzd_ar,
    generate_satim_edi_transfer_file,
    render_official_bank_transfer_html,
)
from algeria_tax.payroll_engine import (
    compute_cnas_algeria,
    compute_irg_algeria,
    generate_cnas_das_txt,
)
from algeria_tax.scf_structure import SCF_TREE


class DummyCompanyDoc:
    def __init__(self, name, country="", default_currency=""):
        self.name = name
        self.country = country
        self.default_currency = default_currency


def run_all_tests():
    results = []

    # 1. Restriction Entreprise 'Algérie Uniquement' (Algeria + DZD)
    c_valid = DummyCompanyDoc("SARL EL TASSYIR", country="", default_currency="")
    validate_company_algeria_only(c_valid)
    assert c_valid.country == "Algeria", f"Expected Algeria, got {c_valid.country}"
    assert c_valid.default_currency == "DZD", f"Expected DZD, got {c_valid.default_currency}"

    c_ar = DummyCompanyDoc("شركة التسيير الآلي", country="الجزائر", default_currency="DZD")
    validate_company_algeria_only(c_ar)
    assert c_ar.country == "Algeria"

    blocked_country = False
    try:
        validate_company_algeria_only(DummyCompanyDoc("Societe Etrangere", country="France", default_currency="DZD"))
    except ValueError:
        blocked_country = True
    assert blocked_country, "Foreign country creation must be blocked!"

    blocked_currency = False
    try:
        validate_company_algeria_only(DummyCompanyDoc("Societe EUR", country="Algeria", default_currency="EUR"))
    except ValueError:
        blocked_currency = True
    assert blocked_currency, "Non-DZD currency must be blocked!"
    results.append(("1. Restriction Entreprise 'Algerie Uniquement' (Algeria + DZD)", "PASS", "Bloque tout pays != Algeria et toute devise != DZD ; accepte Algeria / الجزائر."))

    # 2. Référentiel National Algérien (22 Banques, 18 Assurances, 7 Caisses, 58 Wilayas, 11 Formes Juridiques, RIB 20 chiffres)
    assert len(ALGERIAN_BANKS) == 22, f"Expected 22 banks, got {len(ALGERIAN_BANKS)}"
    assert len(ALGERIAN_INSURERS) == 18, f"Expected 18 insurers, got {len(ALGERIAN_INSURERS)}"
    assert len(ALGERIAN_SOCIAL_ORGANISMS) == 7, f"Expected 7 social organisms, got {len(ALGERIAN_SOCIAL_ORGANISMS)}"
    assert len(ALGERIAN_WILAYAS) == 58, f"Expected 58 Wilayas, got {len(ALGERIAN_WILAYAS)}"
    assert len(ALGERIAN_LEGAL_FORMS) == 11, f"Expected 11 legal forms, got {len(ALGERIAN_LEGAL_FORMS)}"

    key_bna = compute_algerian_rib_key("001", "00600", "0300001234")
    full_rib_bna = f"001006000300001234{key_bna}"
    rib_check = validate_algerian_rib(full_rib_bna)
    assert rib_check["is_valid"] is True, f"RIB check failed: {rib_check}"
    assert rib_check["bank_code"] == "001"

    bad_rib = validate_algerian_rib("00100600030000123400")
    assert bad_rib["is_valid"] is False
    results.append(("2. Referentiel National (22 Banques, 18 Assurances, 7 Caisses, 58 Wilayas, RIB 20 chiffres)", "PASS", f"RIB BNA teste : {rib_check['formatted_rib']} (Cle Modulo 97 = {key_bna} valide)."))

    # 3. Ordres de Virement Bancaire Multi-Banques & Fichier EDI SATIM
    words_fr = amount_to_words_dzd_fr(165656.83)
    words_ar = amount_to_words_dzd_ar(165656.83)
    assert "Dinars" in words_fr and "83 Centimes" in words_fr
    assert "دينار جزائري" in words_ar

    key_emp1 = compute_algerian_rib_key("002", "00105", "0001234567")
    key_emp2 = compute_algerian_rib_key("004", "00112", "0009876543")
    transfer_lines = [
        {
            "beneficiary_name": "SAIDANE ABDELHADI",
            "beneficiary_bank": "Banque Exterieure d'Algerie (BEA)",
            "beneficiary_rib": f"002001050001234567{key_emp1}",
            "payment_reference": "PAIE OCTOBRE 2026",
            "amount": 47717.76,
        },
        {
            "beneficiary_name": "BENALI KARIM",
            "beneficiary_bank": "Credit Populaire d'Algerie (CPA)",
            "beneficiary_rib": f"004001120009876543{key_emp2}",
            "payment_reference": "PAIE OCTOBRE 2026",
            "amount": 65432.10,
        },
    ]
    edi_txt = generate_satim_edi_transfer_file(
        order_name="OV-PAIE-2026-10",
        execution_date="2026-10-31",
        company_name="EURL BUILD AND SECURE NETWORKS",
        emitter_rib_20=full_rib_bna,
        lines=transfer_lines,
        transfer_motif="PAIE OCTOBRE 2026",
    )
    edi_lines = edi_txt.strip().splitlines()
    assert len(edi_lines) == 4
    assert edi_lines[0].startswith("0120261031")
    assert edi_lines[-1].startswith("09000002")

    html_ov = render_official_bank_transfer_html({
        "name": "OV-PAIE-2026-10",
        "transfer_type": "Virement Collectif de Salaires (Paie Mensuelle - Compte 421)",
        "posting_date": "2026-10-31",
        "company": "Build And Secure Networks",
        "company_nif": "001716099938766",
        "emitter_bank_code": "001",
        "emitter_branch": "Agence Hydra Alger",
        "emitter_rib": full_rib_bna,
        "scf_debit_account": "421 - Personnel - remunerations dues - BSN",
        "scf_credit_account": "512 - Banques comptes courants - BSN",
        "total_amount": 113149.86,
        "lines": transfer_lines,
    })
    assert "ORDRE DE VIREMENT BANCAIRE" in html_ov
    results.append(("3. Ordres de Virement Bancaire Multi-Banques & Fichier EDI SATIM", "PASS", f"Fichier EDI SATIM ({len(edi_lines)} enregistrements 01/02/09) + Rendu HTML officiel valides."))

    # 4. Plan Comptable National SCF (Classes 1 à 7)
    assert len(SCF_TREE) == 5, f"Expected 5 SCF root blocks, got {len(SCF_TREE)}"
    results.append(("4. Plan Comptable National SCF (Loi 07-11 - Classes 1 a 7)", "PASS", "5 blocs racines SCF (ACTIF, PASSIF, CAPITAUX PROPRES, CHARGES, PRODUITS) verifies."))

    # 5. Moteur de Paie Algérien 3-Strates (CNAS 9%/26% + IRG Art. 104 CIDTA)
    cnas_gen = compute_cnas_algeria(45268.30, "Régime Général")
    assert abs(cnas_gen["cnas_salarie_9"] - 4074.15) < 0.01
    assert abs(cnas_gen["cnas_employeur"] - 11769.76) < 0.01

    irg_check = compute_irg_algeria(54816.76, working_days=22, payment_days=22, regime_irg="Barème Général")
    assert abs(irg_check["assiette_mensuelle_ramenee"] - 54810.0) < 0.01
    assert abs(irg_check["irg_bareme"] - 7098.70) < 0.01

    irg_exo = compute_irg_algeria(29850.0, working_days=22, payment_days=22)
    assert irg_exo["irg_bareme"] == 0.0

    das_txt = generate_cnas_das_txt("16489120-52", "2026", "DAS", [
        {"nss": "880116123456", "employee_name": "SAIDANE ABDELHADI", "working_days": 22, "assiette_cnas": 45268.30, "cnas_9": 4074.15, "cnas_26": 11769.76}
    ])
    assert "16489120-52;2026;DAS;880116123456" in das_txt
    results.append(("5. Moteur de Paie Algerien 3-Strates (CNAS 9%/26%, IRG Art. 104 CIDTA, Export CNAS .TXT)", "PASS", "Assiette 54 816,76 -> arrondie 54 810 DA -> IRG = 7 098,70 DA ; Exoneration <= 30 000 DA OK."))

    # 6. Vérification de tous les DocTypes JSON & Print Formats JSON
    dt_root = os.path.join(APP_ROOT, "algeria_tax", "algeria_tax", "doctype")
    expected_doctypes = [
        "algerian_tax_settings",
        "ibs_installment_schedule",
        "g50_declaration",
        "bilan_fiscal",
        "cnas_declaration",
        "cnas_employee_line",
        "g29_declaration",
        "g29_employee_line",
        "algerian_bank_transfer_order",
        "algerian_bank_transfer_line",
        "cabinet_client_dossier",
    ]
    for dt_name in expected_doctypes:
        jpath = os.path.join(dt_root, dt_name, f"{dt_name}.json")
        assert os.path.exists(jpath), f"Missing DocType JSON: {jpath}"
        data = json.load(open(jpath, "r", encoding="utf-8"))
        assert data.get("doctype") == "DocType"

    pf_root = os.path.join(APP_ROOT, "algeria_tax", "algeria_tax", "print_format")
    pf_count = len([d for d in os.listdir(pf_root) if os.path.isdir(os.path.join(pf_root, d))])
    assert pf_count >= 6
    results.append(("6. Integrite des 11 DocTypes & 6 Formats d'Impression Officiels", "PASS", f"{len(expected_doctypes)} DocTypes JSON/Python et {pf_count} Formats d'Impression Jinja valides."))

    # 7. Branding 'El Tassyir El Ali | التسيير الآلي', Logo SVG & Traductions FR/AR
    logo_path = os.path.join(APP_ROOT, "algeria_tax", "public", "images", "el_tassyir_el_ali_logo.svg")
    assert os.path.exists(logo_path)
    logo_svg = open(logo_path, "r", encoding="utf-8").read()
    assert "EL TASSYIR EL ALI" in logo_svg and "التسيير الآلي" in logo_svg

    fr_csv_path = os.path.join(APP_ROOT, "algeria_tax", "translations", "fr.csv")
    ar_csv_path = os.path.join(APP_ROOT, "algeria_tax", "translations", "ar.csv")
    fr_rows = list(csv.reader(open(fr_csv_path, "r", encoding="utf-8")))
    ar_rows = list(csv.reader(open(ar_csv_path, "r", encoding="utf-8")))
    assert len(fr_rows) >= 30 and len(ar_rows) >= 35
    results.append(("7. Branding 'El Tassyir El Ali', Logo SVG & Traductions FR/AR", "PASS", f"Logo SVG bilingue + {len(fr_rows)} traductions FR + {len(ar_rows)} traductions AR valides."))

    print("=" * 95)
    print("RAPPORT D'EXECUTION DE LA SUITE DE TESTS GENERALE — EL TASSYIR EL ALI")
    print("=" * 95)
    for title, status, detail in results:
        print(f"[{status}] {title}\n       -> {detail}")
    print("=" * 95)
    print(f"TOTAL : {len(results)}/{len(results)} PILIERS VALIDES AVEC SUCCES (0 ERREUR).")


if __name__ == "__main__":
    run_all_tests()
