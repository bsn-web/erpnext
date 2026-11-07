# -*- coding: utf-8 -*-
# Copyright (c) 2026, Algeria Tax & SCF Compliance
# Référentiel Officiel : Loi 90-11 (Droit du Travail), Loi 83-14 & Décret 96-208 (Assiette CNAS),
# Loi 06-21 (Abattements CNAS), CIDTA Art. 66 à 75 & 104 (Barème IRG Salaires LF 2022-2026)

try:
    import frappe
    from frappe.utils import flt
except ImportError:
    class _DummyFrappe:
        db = None
        @staticmethod
        def whitelist(*args, **kwargs):
            def _dec(fn):
                return fn
            return _dec
    frappe = _DummyFrappe()
    def flt(val):
        try:
            return float(val or 0.0)
        except Exception:
            return 0.0

# Classification officielle des rubriques selon le Décret exécutif n° 96-208 (CNAS) et Art. 67-68 CIDTA (IRG)
STRATE_1_COTISABLE_IMPOSABLE_ABBRS = {
    "S_B", "SB", "B", "IEP", "NUIS", "I.F.S.P", "IFSP", "RESP",
    "P.R.I", "PRI", "P.R.C", "PRC", "HS", "ICP", "LE", "A", "SCD", "SvCD", "I.C.R",
}
STRATE_1BIS_COTISABLE_IRG_10_ABBRS = {"PRI_PER"}
STRATE_2_NON_COTISABLE_IMPOSABLE_ABBRS = {"pan", "PAN", "PT", "TRANSP", "IUVP"}
STRATE_3_NON_COTISABLE_NON_IMPOSABLE_ABBRS = {
    "SAL.UNIQ", "SAL_UNIQ", "ALLO.FAM/CNAS", "ALLOC_FAM", "IZCV", "MISSION",
}


def compute_irg_bareme_mensuel(revenu_mensuel_30j, is_handicape_retraite=False):
    """
    Calcule l'IRG mensuel théorique (base mois complet) selon l'Article 104 du CIDTA (LF 2022-2026) :
    1. Arrondi de l'assiette à la dizaine de dinars inférieure (Art. 104 CIDTA)
    2. Exonération totale si R <= 30 000 DZD
    3. Barème progressif par tranches (0%, 23%, 27%, 30%, 33%, 35%)
    4. 1er Abattement de 40% encadré entre 1 000 DZD (min) et 1 500 DZD (max)
    5. 2ème Abattement dégressif de lissage :
       - Régime général (30 000 < R <= 35 000 DZD) : IRG = IRG_1 * (137/51) - (27925/8)
       - Régime Handicapé / Retraité (30 000 < R <= 42 500 DZD) : IRG = IRG_1 * (93/61) - (81213/41)
    """
    r = int(max(0.0, flt(revenu_mensuel_30j)) // 10) * 10.0
    if r <= 30000.0:
        return {
            "assiette_arrondie_10": r,
            "irg_brut": 0.0,
            "abattement_40": 0.0,
            "irg_apres_1er_abatt": 0.0,
            "irg_mensuel_retenu": 0.0,
        }

    # Calcul par tranches
    if r <= 20000.0:
        irg_brut = 0.0
    elif r <= 40000.0:
        irg_brut = (r - 20000.0) * 0.23
    elif r <= 80000.0:
        irg_brut = 4600.0 + (r - 40000.0) * 0.27
    elif r <= 160000.0:
        irg_brut = 15400.0 + (r - 80000.0) * 0.30
    elif r <= 320000.0:
        irg_brut = 39400.0 + (r - 160000.0) * 0.33
    else:
        irg_brut = 92200.0 + (r - 320000.0) * 0.35

    # 1er Abattement 40% (Min 1 000 DZD / Max 1 500 DZD)
    abatt_40 = min(1500.0, max(1000.0, irg_brut * 0.40))
    irg_1 = max(0.0, irg_brut - abatt_40)

    # 2ème Abattement dégressif (LF 2022-2026)
    if is_handicape_retraite and r <= 42500.0:
        irg_final = max(0.0, irg_1 * (93.0 / 61.0) - (81213.0 / 41.0))
    elif not is_handicape_retraite and r <= 35000.0:
        irg_final = max(0.0, irg_1 * (137.0 / 51.0) - (27925.0 / 8.0))
    else:
        irg_final = irg_1

    return {
        "assiette_arrondie_10": r,
        "irg_brut": round(irg_brut, 2),
        "abattement_40": round(abatt_40, 2),
        "irg_apres_1er_abatt": round(irg_1, 2),
        "irg_mensuel_retenu": round(irg_final, 2),
    }


@frappe.whitelist()
def compute_irg_algeria(
    assiette_imposable,
    working_days=22.0,
    payment_days=22.0,
    regime_irg="Barème Général",
    base_primes_10_pct=0.0,
):
    """
    Calcule l'IRG total du bulletin (Barème progressif proratisé selon Circulaire DGI + Taux proportionnel 10%).
    """
    assiette = max(0.0, flt(assiette_imposable))
    w_days = flt(working_days) or 22.0
    p_days = flt(payment_days) or w_days
    if p_days <= 0:
        p_days = w_days

    reg_str = str(regime_irg or "")
    if "Exonéré IRG" in reg_str:
        return {
            "assiette_imposable_effective": assiette,
            "assiette_mensuelle_ramenee": assiette,
            "irg_bareme": 0.0,
            "irg_10_pct": 0.0,
            "irg_total": 0.0,
        }
    if "Consultant" in reg_str or "10% Libératoire" in reg_str:
        irg_10 = round((assiette + flt(base_primes_10_pct)) * 0.10, 2)
        return {
            "assiette_imposable_effective": assiette,
            "assiette_mensuelle_ramenee": assiette,
            "irg_bareme": 0.0,
            "irg_10_pct": irg_10,
            "irg_total": irg_10,
        }

    is_handi = ("Handicapé" in reg_str or "Retraité" in reg_str or "42 500" in reg_str)

    # Circulaire DGI : ramener l'assiette imposable au mois complet si absence / entrée-sortie
    ratio_mois = (w_days / p_days) if (p_days < w_days and p_days > 0) else 1.0
    assiette_mensuelle = assiette * ratio_mois

    res_mensuel = compute_irg_bareme_mensuel(assiette_mensuelle, is_handicape_retraite=is_handi)
    irg_proratise = round(res_mensuel["irg_mensuel_retenu"] / ratio_mois, 2)

    # IRG proportionnel à 10% (sans abattement) sur primes de rendement périodiques (Art. 104 CIDTA)
    irg_10 = round(max(0.0, flt(base_primes_10_pct)) * 0.10, 2)

    return {
        "assiette_imposable_effective": round(assiette, 2),
        "assiette_mensuelle_ramenee": res_mensuel["assiette_arrondie_10"],
        "irg_brut_mensuel": res_mensuel["irg_brut"],
        "abattement_40_mensuel": res_mensuel["abattement_40"],
        "irg_bareme": irg_proratise,
        "irg_10_pct": irg_10,
        "irg_total": round(irg_proratise + irg_10, 2),
    }


@frappe.whitelist()
def compute_cnas_algeria(assiette_cotisable, regime_cnas="Régime Général"):
    """
    Calcule les cotisations CNAS Salarié (9%) et Employeur (26% ou taux réduit Loi 06-21).
    """
    base_ss = max(0.0, flt(assiette_cotisable))
    reg = str(regime_cnas or "")
    if "CASNOS" in reg or "0% CNAS" in reg:
        return {"assiette_cnas": base_ss, "cnas_salarie_9": 0.0, "taux_employeur": 0.0, "cnas_employeur": 0.0, "total_cnas": 0.0}

    taux_salarie = 9.0
    if "-56%" in reg or "11.44%" in reg:
        taux_emp = 11.44
    elif "-80%" in reg or "5.20%" in reg:
        taux_emp = 5.20
    elif "-90%" in reg or "2.60%" in reg:
        taux_emp = 2.60
    else:
        taux_emp = 26.0

    part_sal = round(base_ss * taux_salarie / 100.0, 2)
    part_emp = round(base_ss * taux_emp / 100.0, 2)
    return {
        "assiette_cnas": round(base_ss, 2),
        "cnas_salarie_9": part_sal,
        "taux_employeur": taux_emp,
        "cnas_employeur": part_emp,
        "total_cnas": round(part_sal + part_emp, 2),
    }


@frappe.whitelist()
def compute_solde_tout_compte_dz(employee, cumul_brut_cotisable_periode, jours_conges_restants=0.0, salaire_mensuel_base=0.0):
    """
    Calcule l'Indemnité de Congés Payés (ICP = 1/12e des gains cotisables - Art. 52 Loi 90-11)
    et le Solde de Tout Compte (STC) conformément à la Loi 90-11.
    """
    icp_1_12 = round(flt(cumul_brut_cotisable_periode) / 12.0, 2)
    icp_jours = round((flt(salaire_mensuel_base) / 30.0) * flt(jours_conges_restants), 2)
    icp_retenue = max(icp_1_12, icp_jours)
    cnas_9 = round(icp_retenue * 0.09, 2)
    assiette_irg = icp_retenue - cnas_9
    irg_info = compute_irg_algeria(assiette_irg)
    net_stc = round(icp_retenue - cnas_9 - irg_info["irg_total"], 2)
    return {
        "employee": employee,
        "icp_1_12e": icp_1_12,
        "icp_jours_restants": icp_jours,
        "icp_brute_retenue": icp_retenue,
        "cnas_salarie_9": cnas_9,
        "assiette_irg": assiette_irg,
        "irg_retenu": irg_info["irg_total"],
        "net_stc_a_payer": net_stc,
    }


def analyze_salary_slip_strata(slip_doc):
    """
    Analyse les lignes d'un Salary Slip et calcule les 3 strates réglementaires algériennes
    (Strate 1 Cotisable & Imposable, Strate 2 Imposable Non Cotisable, Strate 3 Non Imposable).
    """
    strate_1 = 0.0
    strate_1bis_pri_per = 0.0
    strate_2 = 0.0
    strate_3 = 0.0

    for e in (slip_doc.get("earnings") or []):
        if getattr(e, "statistical_component", 0) or getattr(e, "do_not_include_in_total", 0):
            continue
        abbr = (e.abbr or "").strip()
        comp = (e.salary_component or "").strip()
        if comp in ("salaire de poste", "imposable", "Assiette Cotisable CNAS (Salaire de Poste)", "Assiette Imposable IRG Barème", "Cotisations Patronales (CNAS 26%)"):
            continue
        amt = flt(e.amount)
        if abbr in STRATE_1BIS_COTISABLE_IRG_10_ABBRS:
            strate_1 += amt
            strate_1bis_pri_per += amt
        elif abbr in STRATE_2_NON_COTISABLE_IMPOSABLE_ABBRS or "panier" in comp.lower() or "transport" in comp.lower():
            strate_2 += amt
        elif abbr in STRATE_3_NON_COTISABLE_NON_IMPOSABLE_ABBRS or "unique" in comp.lower() or "familiale" in comp.lower() or "mission" in comp.lower() or "zone" in comp.lower():
            strate_3 += amt
        else:
            strate_1 += amt

    cnas_9 = 0.0
    irg_bar = 0.0
    irg_10 = 0.0
    for d in (slip_doc.get("deductions") or []):
        comp = (d.salary_component or "").strip()
        abbr = (d.abbr or "").strip()
        if comp in ("irgbrut", "abattement irg"):
            continue
        amt = flt(d.amount)
        if "CNAS" in comp or abbr in ("CNAS", "Cnas"):
            cnas_9 += amt
        elif abbr == "IRG_10" or "10%" in comp:
            irg_10 += amt
        elif "Impôt sur le revenu global" in comp or abbr in ("IRG", "IRG_1"):
            irg_bar += amt

    if cnas_9 == 0.0 and strate_1 > 0:
        cnas_9 = round(strate_1 * 0.09, 2)

    regime_cnas = "Régime Général"
    if slip_doc.employee and frappe.db.exists("Employee", slip_doc.employee):
        regime_cnas = frappe.db.get_value("Employee", slip_doc.employee, "custom_regime_cotisation_cnas") or "Régime Général"

    cnas_info = compute_cnas_algeria(strate_1, regime_cnas=regime_cnas)
    assiette_irg_legale = max(0.0, (strate_1 - strate_1bis_pri_per) * 0.91 + strate_2)

    return {
        "custom_assiette_cnas": round(strate_1, 2),
        "custom_cnas_salarie_9": round(cnas_9, 2),
        "custom_cnas_employeur_26": cnas_info["cnas_employeur"],
        "custom_total_imposable_non_cotisable": round(strate_2, 2),
        "custom_assiette_irg": round(assiette_irg_legale, 2),
        "custom_irg_bareme": round(irg_bar, 2),
        "custom_irg_10_pct": round(irg_10, 2),
        "custom_total_non_imposable": round(strate_3, 2),
    }


def get_paid_leave_days_in_period(employee, start_date, end_date):
    """
    Calcule le nombre de jours de congés payés (hors LWP) pris par le salarié sur la période du bulletin.
    Selon le Décret exécutif n° 96-208, les indemnités de Panier et de Transport sont liées à la présence
    effective au poste et ne sont pas dues pendant les congés annuels ou spéciaux.
    """
    if not employee or not start_date or not end_date:
        return 0.0
    leaves = frappe.db.sql("""
        SELECT la.total_leave_days, lt.is_lwp
        FROM `tabLeave Application` la
        INNER JOIN `tabLeave Type` lt ON lt.name = la.leave_type
        WHERE la.employee = %s
          AND la.docstatus = 1
          AND la.status = 'Approved'
          AND lt.is_lwp = 0
          AND la.from_date <= %s
          AND la.to_date >= %s
    """, (employee, end_date, start_date), as_dict=True)
    return sum(flt(l.total_leave_days) for l in leaves)


def on_salary_slip_validate(doc, method=None):
    """
    Hook sur Salary Slip.validate (uniquement sur brouillons docstatus == 0 pour ne jamais toucher à l'historique) :
    1. Proratise Panier (pan) et Transport (PT) sur les jours de présence effective (payment_days - congés payés) (Décret 96-208).
    2. Applique les régimes spéciaux CNAS (Loi 06-21 : 11.44%, 5.20%, 2.60%) sur CNAS-E et CNAS_P_431.
    3. Applique l'arrondi à la dizaine inférieure (Art. 104 CIDTA) et les régimes spéciaux IRG (Handicapé/Retraité 42 500 DA, Sud, 10%) sur la ligne IRG.
    4. Alimente les 8 champs d'audit des 3 strates algériennes.
    """
    if doc.docstatus != 0:
        return

    if getattr(doc, "salary_structure", None) == "Structure Paie Algérie SCF 2026":
        w_days = flt(doc.total_working_days) or 22.0
        p_days = flt(doc.payment_days) or w_days
        paid_leaves = get_paid_leave_days_in_period(doc.employee, doc.start_date, doc.end_date)
        effective_presence_days = max(0.0, p_days - paid_leaves)

        # Fix 3 : Si le salarié a pris des congés payés, proratiser Panier & Transport sur la présence effective
        if paid_leaves > 0 and w_days > 0:
            for e in (doc.get("earnings") or []):
                if e.abbr == "pan":
                    e.amount = round(6000.0 * (effective_presence_days / w_days), 2)
                elif e.abbr == "PT":
                    e.amount = round(7622.31 * (effective_presence_days / w_days), 2)

        vals = analyze_salary_slip_strata(doc)
        ass_cnas = vals["custom_assiette_cnas"]
        ass_irg = vals["custom_assiette_irg"]

        regime_cnas = "Régime Général"
        regime_irg = "Barème Général"
        if doc.employee and frappe.db.exists("Employee", doc.employee):
            emp_vals = frappe.db.get_value(
                "Employee", doc.employee,
                ["custom_regime_cotisation_cnas", "custom_situation_fiscale_irg"],
                as_dict=True
            ) or {}
            regime_cnas = emp_vals.get("custom_regime_cotisation_cnas") or "Régime Général"
            regime_irg = emp_vals.get("custom_situation_fiscale_irg") or "Barème Général"

        cnas_res = compute_cnas_algeria(ass_cnas, regime_cnas=regime_cnas)
        pri_per_amt = sum(flt(e.amount) for e in (doc.get("earnings") or []) if e.abbr == "PRI_PER")
        irg_res = compute_irg_algeria(
            ass_irg,
            working_days=w_days,
            payment_days=p_days,
            regime_irg=regime_irg,
            base_primes_10_pct=pri_per_amt * 0.91,
        )

        # Fix 4 : Synchroniser les montants sur les lignes du bulletin
        for e in (doc.get("earnings") or []):
            if e.abbr == "ASS_CNAS":
                e.amount = ass_cnas
            elif e.abbr == "ASS_IRG":
                e.amount = flt(irg_res.get("assiette_mensuelle_ramenee") or ass_irg)
            elif e.abbr == "CNAS-E":
                e.amount = cnas_res["cnas_employeur"]

        for d in (doc.get("deductions") or []):
            if d.abbr == "CNAS":
                d.amount = cnas_res["cnas_salarie_9"]
            elif d.abbr == "CNAS_P_431":
                d.amount = cnas_res["cnas_employeur"]
            elif d.abbr == "IRG":
                d.amount = irg_res["irg_bareme"]
            elif d.abbr == "IRG_10":
                d.amount = irg_res["irg_10_pct"]

        doc.gross_pay = round(sum(
            flt(e.amount) for e in (doc.get("earnings") or [])
            if not getattr(e, "statistical_component", 0) and not getattr(e, "do_not_include_in_total", 0)
        ), 2)
        doc.total_deduction = round(sum(
            flt(d.amount) for d in (doc.get("deductions") or [])
            if not getattr(d, "statistical_component", 0) and not getattr(d, "do_not_include_in_total", 0)
        ), 2)
        doc.net_pay = round(doc.gross_pay - doc.total_deduction, 2)
        doc.rounded_total = round(doc.net_pay)

        vals["custom_cnas_employeur_26"] = cnas_res["cnas_employeur"]
        vals["custom_irg_bareme"] = irg_res["irg_bareme"]
        vals["custom_irg_10_pct"] = irg_res["irg_10_pct"]
        for k, v in vals.items():
            setattr(doc, k, v)
    else:
        vals = analyze_salary_slip_strata(doc)
        for k, v in vals.items():
            setattr(doc, k, v)


# === POINT 6 : RECTIFICATION AUTOMATIQUE CLOTURE 2026 / OUVERTURE 2027 ===

@frappe.whitelist()
def compute_2026_payroll_gl_anomaly(company="Build And Secure Networks"):
    """
    Calcule au centime près l'anomalie des écritures historiques ACC-JV-2026-00001 et ACC-JV-2026-00004 du 01/03/2026 :
    - Surévaluation nette des charges P&L 2026 (631 + 5216 - 636 vs Brut réel) = 76 770,92 DZD (à réintégrer au Tableau 9 du Bilan Fiscal 2026)
    - Soldes de Bilan erronés à purger au 01/01/2027 par le compte 14 - Report à nouveau (Art. 138-4 SCF) :
      * Débit 421 - Personnel – rémunérations dues - BSN : 72 523,65 DZD
      * Débit 2130 - IRG - BSN : 11 840,00 DZD
      * Crédit 431 - Sécurité sociale (CNAS) - BSN : 7 592,73 DZD
      * Crédit 14 - Report à nouveau - BSN : 76 770,92 DZD
    """
    vouchers = ("ACC-JV-2026-00001", "ACC-JV-2026-00004")
    gl_rows = frappe.db.sql("""
        SELECT account, SUM(debit) AS debit, SUM(credit) AS credit
        FROM `tabGL Entry`
        WHERE company = %s AND is_cancelled = 0 AND voucher_no IN %s
        GROUP BY account
    """, (company, vouchers), as_dict=True)

    if not gl_rows:
        return {"has_anomaly": False, "reintegration_tab9_2026": 0.0}

    by_acc = {r.account: (flt(r.debit), flt(r.credit)) for r in gl_rows}
    d_631 = by_acc.get("631 - Rémunération du personnel - BSN", (0.0, 0.0))[0]
    d_5216 = by_acc.get("5216 - Travel Expenses - BSN", (0.0, 0.0))[0]
    c_636 = by_acc.get("636 - Charges sociales de l'exploitant individuel - BSN", (0.0, 0.0))[1]
    c_2130 = by_acc.get("2130 - IRG - BSN", (0.0, 0.0))[1]
    d_421, c_421 = by_acc.get("421 - Personnel – rémunérations dues - BSN", (0.0, 0.0))
    net_c_421 = round(c_421 - d_421, 2)

    # Vrais montants des 2 bulletins de Janvier et Février 2026 (Sal Slip/HR-EMP-00008/00002 & 00003)
    true_gross_631 = 41153.00 + 56832.96  # 97 985,96 DZD
    true_net_421 = 34936.23 + 50000.00    # 84 936,23 DZD
    true_cnas_431 = round(c_636, 2)       # 7 592,73 DZD

    recorded_pnl_net = round(d_631 + d_5216 - c_636, 2)  # 174 756,88 DZD
    sur_eval_pnl_2026 = round(recorded_pnl_net - true_gross_631, 2)  # 76 770,92 DZD
    trop_credite_421 = round(net_c_421 - true_net_421, 2)            # 72 523,65 DZD

    return {
        "has_anomaly": sur_eval_pnl_2026 > 0,
        "reintegration_tab9_2026": sur_eval_pnl_2026,
        "debit_421": trop_credite_421,
        "debit_2130": round(c_2130, 2),
        "credit_431": true_cnas_431,
        "credit_110_ran": sur_eval_pnl_2026,
        "total_ecriture_2027": round(trop_credite_421 + c_2130, 2),
    }


@frappe.whitelist()
def trigger_2027_opening_rectification_je(company="Build And Secure Networks", auto_submit=False, trigger_source="Clôture Exercice 2026"):
    """
    Crée (et soumet automatiquement lors de la clôture de l'exercice 2026) l'écriture d'Opération Diverse
    d'ouverture au 01/01/2027 (Art. 138-4 du SCF : Correction d'erreurs sur exercices antérieurs via Report à nouveau).
    """
    info = compute_2026_payroll_gl_anomaly(company)
    if not info.get("has_anomaly"):
        return {"status": "no_anomaly"}

    if not frappe.db.exists("Fiscal Year", "2027"):
        fy = frappe.new_doc("Fiscal Year")
        fy.year = "2027"
        fy.year_start_date = "2027-01-01"
        fy.year_end_date = "2027-12-31"
        fy.insert(ignore_permissions=True)

    ref_no = "RECTIF-SCF-138-4-PAIE-2026"
    existing_je = frappe.get_all(
        "Journal Entry",
        filters={"company": company, "cheque_no": ref_no, "docstatus": ["!=", 2]},
        fields=["name", "docstatus"],
        limit=1,
    )

    if existing_je:
        je_doc = frappe.get_doc("Journal Entry", existing_je[0].name)
        if auto_submit and je_doc.docstatus == 0:
            je_doc.submit()
            return {"status": "submitted", "journal_entry": je_doc.name}
        return {"status": "exists", "journal_entry": je_doc.name, "docstatus": je_doc.docstatus}

    ran_account = "14 - Report à nouveau - BSN"
    if not frappe.db.exists("Account", ran_account):
        ran_account = "SCF-110 - Report à nouveau (solde créditeur) - BSN"

    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = company
    je.posting_date = "2027-01-01"
    je.cheque_no = ref_no
    je.cheque_date = "2027-01-01"
    je.user_remark = (
        f"[DÉCLENCHEUR AUTOMATIQUE — {trigger_source}] "
        "Rectification à l'ouverture 2027 (Art. 138-4 du SCF) des comptes de Bilan 421, 2130 et 431 "
        "suite aux écritures historiques ACC-JV-2026-00001 et ACC-JV-2026-00004 du 01/03/2026, "
        "dont la surcharge P&L (+76 770,92 DZD) a été réintégrée au Tableau 9 du Bilan Fiscal 2026."
    )

    je.append("accounts", {
        "account": "421 - Personnel – rémunérations dues - BSN",
        "debit_in_account_currency": info["debit_421"],
        "credit_in_account_currency": 0.0,
        "user_remark": "Extourne du trop-crédité 421 (doublon salaire de poste & lignes statistiques Janv/Fév 2026)",
    })
    je.append("accounts", {
        "account": "2130 - IRG - BSN",
        "debit_in_account_currency": info["debit_2130"],
        "credit_in_account_currency": 0.0,
        "user_remark": "Solde à zéro du compte 2130 crédité à tort pour irgbrut + abattement irg (5 618 + 6 222)",
    })
    je.append("accounts", {
        "account": "431 - Sécurité sociale (CNAS) - BSN",
        "debit_in_account_currency": 0.0,
        "credit_in_account_currency": info["credit_431"],
        "user_remark": "Rétablissement de la dette CNAS Salarié 9% (imputée à tort en 636 le 01/03/2026)",
    })
    je.append("accounts", {
        "account": ran_account,
        "debit_in_account_currency": 0.0,
        "credit_in_account_currency": info["credit_110_ran"],
        "user_remark": "Correction d'erreur sur exercice antérieur 2026 (Art. 138-4 SCF — égale à la réintégration Tableau 9 2026)",
    })

    je.insert(ignore_permissions=True)
    if auto_submit:
        je.submit()
    return {"status": "submitted" if auto_submit else "draft_created", "journal_entry": je.name, "docstatus": je.docstatus}


def on_period_closing_voucher_submit(doc, method=None):
    """
    Déclencheur automatique lors de la validation de la clôture d'exercice 2026 (Period Closing Voucher) :
    Valide automatiquement l'écriture d'ouverture du 01/01/2027 (Art. 138-4 SCF).
    """
    if str(getattr(doc, "fiscal_year", "")) == "2026":
        trigger_2027_opening_rectification_je(
            company=doc.company,
            auto_submit=True,
            trigger_source=f"Period Closing Voucher {doc.name} (Clôture 2026)",
        )


def ensure_algeria_erp_indexes():
    """Garantit la présence des index composites métiers ERPNext / Fiscalité Algérienne après chaque bench migrate."""
    import frappe
    specs = [
        ("Account", ["company", "account_number"], "idx_acc_company_accnum"),
        ("Payment Entry", ["company", "docstatus", "posting_date"], "idx_pe_comp_doc_pdate"),
        ("Sales Invoice", ["company", "docstatus", "posting_date"], "idx_si_comp_doc_pdate"),
        ("Purchase Invoice", ["company", "docstatus", "posting_date"], "idx_pi_comp_doc_pdate"),
        ("Lead", ["status", "email_id"], "idx_lead_status_email"),
        ("Employee", ["custom_nss_cnas"], "idx_emp_nss_cnas"),
        ("G50 Declaration", ["company", "fiscal_year"], "idx_g50_comp_fy"),
        ("Bilan Fiscal", ["company", "fiscal_year"], "idx_bf_comp_fy"),
        ("CNAS Declaration", ["company", "fiscal_year"], "idx_cnas_comp_fy"),
        ("G29 Declaration", ["company", "fiscal_year"], "idx_g29_comp_fy"),
    ]
    for dt, fields, idx_name in specs:
        try:
            frappe.db.add_index(dt, fields, index_name=idx_name)
        except Exception:
            pass


@frappe.whitelist()
def generate_cnas_das_txt(numero_employeur_cnas, fiscal_year, declaration_type="DAS", employees=None):
    """
    Génère le fichier magnétique officiel (.TXT) pour le portail teledeclaration.cnas.dz (DAC mensuelle / DAS annuelle).
    Format normalisé : N_EMPLOYEUR;ANNEE;TYPE;NSS_12;NOM_PRENOM;JOURS;ASSIETTE_CNAS;PART_SALARIE_9;PART_PATRONALE_26;TOTAL_35
    """
    lines = []
    for emp in (employees or []):
        nss = str(emp.get("nss") or emp.get("nss_cnas") or "").strip()
        nom = str(emp.get("employee_name") or "").strip().upper()
        jours = flt(emp.get("working_days", 22))
        ass = round(flt(emp.get("assiette_cnas", 0.0)), 2)
        c9 = round(flt(emp.get("cnas_9") or emp.get("cnas_salarie_9") or round(ass * 0.09, 2)), 2)
        c26 = round(flt(emp.get("cnas_26") or emp.get("cnas_employeur_26") or round(ass * 0.26, 2)), 2)
        tot = round(c9 + c26, 2)
        lines.append(f"{numero_employeur_cnas};{fiscal_year};{declaration_type};{nss};{nom};{jours:.1f};{ass:.2f};{c9:.2f};{c26:.2f};{tot:.2f}")
    return "\r\n".join(lines) + ("\r\n" if lines else "")
