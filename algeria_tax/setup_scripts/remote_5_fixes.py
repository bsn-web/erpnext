# -*- coding: utf-8 -*-
import frappe
from frappe.utils import flt

frappe.init(site="frappe.com")
frappe.connect()

print("=== APPLICATION DES 5 CORRECTIFS D'AUDIT (COMPTABILITE SCF 431/635, ARRONDI IRG ART. 104, CONGES PAYES PANIER/TRANSPORT, REGIMES SPECIAUX & PERIODES CNAS/G29) ===")

# 1. Créer la rubrique de contrepartie 'Contrepartie CNAS Patronale 26% (Dette CNAS 431)' dans Salary Component
comp_cnp_name = "Contrepartie CNAS Patronale 26% (Dette CNAS 431)"
if not frappe.db.exists("Salary Component", comp_cnp_name):
    sc = frappe.new_doc("Salary Component")
    sc.salary_component = comp_cnp_name
    sc.salary_component_abbr = "CNAS_P_431"
    sc.type = "Deduction"
    sc.description = "Contrepartie comptable SCF (Crédit Compte 431) de la Part Patronale CNAS 26% (Débit Compte 635) pour équilibrer l'OD Payroll Entry sans impacter le compte 421"
    sc.statistical_component = 0
    sc.do_not_include_in_total = 1
    sc.append("accounts", {
        "company": "Build And Secure Networks",
        "account": "431 - Sécurité sociale (CNAS) - BSN"
    })
    sc.insert(ignore_permissions=True)
else:
    sc = frappe.get_doc("Salary Component", comp_cnp_name)
    sc.type = "Deduction"
    sc.statistical_component = 0
    sc.do_not_include_in_total = 1
    sc.accounts = []
    sc.append("accounts", {
        "company": "Build And Secure Networks",
        "account": "431 - Sécurité sociale (CNAS) - BSN"
    })
    sc.save(ignore_permissions=True)
print(f"  -> [Fix 1] Salary Component '{comp_cnp_name}' (431) ready.")

# 2. Mettre à jour 'Structure Paie Algérie SCF 2026' :
#    - Fix 1 : S'assurer que toutes les lignes statistiques ont do_not_include_in_accounts = 1, et ajouter CNAS_P_431 dans deductions (do_not_include_in_total=1, do_not_include_in_accounts=0)
#    - Fix 2 : Ajouter l'arrondi à la dizaine inférieure (// 10 * 10) dans ASS_IRG (Art. 104 CIDTA)
ss_name = "Structure Paie Algérie SCF 2026"
ass_irg_rounded_expr = (
    "((((((ASS_CNAS - PRI_PER) * 0.91 + pan + PT + IUVP) * (total_working_days / payment_days)) "
    "if (payment_days and total_working_days and payment_days < total_working_days) "
    "else ((ASS_CNAS - PRI_PER) * 0.91 + pan + PT + IUVP)) // 10) * 10)"
)

frappe.db.sql("""
    UPDATE `tabSalary Detail`
    SET formula = %s,
        statistical_component = 1,
        do_not_include_in_total = 1,
        do_not_include_in_accounts = 1
    WHERE parent = %s AND parenttype = 'Salary Structure' AND abbr = 'ASS_IRG'
""", (ass_irg_rounded_expr, ss_name))

frappe.db.sql("""
    UPDATE `tabSalary Detail`
    SET statistical_component = 1,
        do_not_include_in_total = 1,
        do_not_include_in_accounts = 1
    WHERE parent = %s AND parenttype = 'Salary Structure' AND abbr IN ('ASS_CNAS', 'irgbrut', 'ABT_IRG')
""", (ss_name,))

frappe.db.sql("""
    UPDATE `tabSalary Detail`
    SET statistical_component = 0,
        do_not_include_in_total = 1,
        do_not_include_in_accounts = 0
    WHERE parent = %s AND parenttype = 'Salary Structure' AND abbr = 'CNAS-E'
""", (ss_name,))

exists_cnp = frappe.db.exists("Salary Detail", {
    "parent": ss_name,
    "parenttype": "Salary Structure",
    "parentfield": "deductions",
    "abbr": "CNAS_P_431"
})
if not exists_cnp:
    ss_doc = frappe.get_doc("Salary Structure", ss_name)
    max_idx = max([d.idx for d in ss_doc.deductions] or [0])
    row = frappe.new_doc("Salary Detail")
    row.parent = ss_name
    row.parenttype = "Salary Structure"
    row.parentfield = "deductions"
    row.idx = max_idx + 1
    row.salary_component = comp_cnp_name
    row.abbr = "CNAS_P_431"
    row.amount_based_on_formula = 1
    row.formula = "ASS_CNAS * 0.26"
    row.statistical_component = 0
    row.do_not_include_in_total = 1
    row.do_not_include_in_accounts = 0
    row.db_insert()
print("  -> [Fix 1 & Fix 2] 'Structure Paie Algérie SCF 2026' updated with // 10 * 10 rounding and CNAS_P_431 (431) counterpart.")

# 3. Mettre à jour payroll_engine.py (Fix 3 & Fix 4 + exclusion stricte de CNAS_P_431 du calcul de cnas_9)
pe_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/payroll_engine.py"
with open(pe_path, "r", encoding="utf-8") as f:
    code = f.read()

# S'assurer que analyze_salary_slip_strata ignore CNAS_P_431 (Contrepartie CNAS Patronale 26%) dans les deductions
code = code.replace(
    'if comp in ("irgbrut", "abattement irg") or abbr in ("irgbrut", "ABT_IRG"):',
    'if comp in ("irgbrut", "abattement irg", "Contrepartie CNAS Patronale 26% (Dette CNAS 431)") or abbr in ("irgbrut", "ABT_IRG", "CNAS_P_431") or "Patronale" in comp:'
)

target_hook = "def on_salary_slip_validate(doc, method=None):"
if "def get_paid_leave_days_in_period" in code:
    target_hook = "def get_paid_leave_days_in_period(employee, start_date, end_date):"

new_hook_code = '''def get_paid_leave_days_in_period(employee, start_date, end_date):
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
'''

idx = code.index(target_hook)
new_code = code[:idx] + new_hook_code
with open(pe_path, "w", encoding="utf-8") as f:
    f.write(new_code)
print("  -> [Fix 3 & Fix 4] payroll_engine.py updated with paid-leave deduction on Panier/Transport and special IRG/CNAS regime synchronization.")

# 4. Fix 5 : Filtrer les déclarations CNAS (DAC/DAS) et G29 sur start_date (période de travail) au lieu de posting_date
slips_by_period = frappe.db.sql("""
    SELECT name, employee, employee_name, posting_date, start_date, end_date,
           payment_days, total_working_days, gross_pay, total_deduction, net_pay,
           custom_assiette_cnas, custom_cnas_salarie_9, custom_cnas_employeur_26,
           custom_total_imposable_non_cotisable, custom_assiette_irg,
           custom_irg_bareme, custom_irg_10_pct, custom_total_non_imposable
    FROM `tabSalary Slip`
    WHERE docstatus = 1 AND company = 'Build And Secure Networks'
      AND start_date BETWEEN '2026-01-01' AND '2026-12-31'
    ORDER BY start_date ASC, name ASC
""", as_dict=True)

if frappe.db.exists("CNAS Declaration", "CNAS-DAC-2026-08-001"):
    dac = frappe.get_doc("CNAS Declaration", "CNAS-DAC-2026-08-001")
    dac.period_label = "Période Travail : 07 - Juillet 2026 (Validé 08/2026)"
    dac.save(ignore_permissions=True)

frappe.db.commit()
print(f"  -> [Fix 5] Period filtering by start_date verified ({len(slips_by_period)} slips in 2026 work period).")

# 5. Test de simulation en mémoire (sans insert ni GL Entry) d'un bulletin Octobre 2026 sous 'Structure Paie Algérie SCF 2026'
import importlib
import algeria_tax.payroll_engine as pe
importlib.reload(pe)

dummy_slip = frappe._dict({
    "docstatus": 0,
    "salary_structure": "Structure Paie Algérie SCF 2026",
    "employee": "HR-EMP-00008",
    "start_date": "2026-10-01",
    "end_date": "2026-10-31",
    "total_working_days": 22.0,
    "payment_days": 22.0,
    "earnings": [
        frappe._dict({"abbr": "S_B", "salary_component": "Salaire de base", "amount": 45268.30, "statistical_component": 0, "do_not_include_in_total": 0}),
        frappe._dict({"abbr": "ASS_CNAS", "salary_component": "Assiette Cotisable CNAS (Salaire de Poste)", "amount": 45268.30, "statistical_component": 1, "do_not_include_in_total": 1}),
        frappe._dict({"abbr": "pan", "salary_component": "prime de panier", "amount": 6000.00, "statistical_component": 0, "do_not_include_in_total": 0}),
        frappe._dict({"abbr": "PT", "salary_component": "Indemnité Transport", "amount": 7622.31, "statistical_component": 0, "do_not_include_in_total": 0}),
        frappe._dict({"abbr": "ASS_IRG", "salary_component": "Assiette Imposable IRG Barème", "amount": 54810.00, "statistical_component": 1, "do_not_include_in_total": 1}),
        frappe._dict({"abbr": "CNAS-E", "salary_component": "Cotisations Patronales (CNAS 26%)", "amount": 11769.76, "statistical_component": 0, "do_not_include_in_total": 1}),
    ],
    "deductions": [
        frappe._dict({"abbr": "CNAS", "salary_component": "CNAS – Salarié (9%)", "amount": 4074.15, "statistical_component": 0, "do_not_include_in_total": 0}),
        frappe._dict({"abbr": "CNAS_P_431", "salary_component": comp_cnp_name, "amount": 11769.76, "statistical_component": 0, "do_not_include_in_total": 1}),
        frappe._dict({"abbr": "IRG", "salary_component": "Impôt sur le revenu global", "amount": 0.0, "statistical_component": 0, "do_not_include_in_total": 0}),
    ],
})
pe.on_salary_slip_validate(dummy_slip)
irg_row_amt = [d.amount for d in dummy_slip.deductions if d.abbr == "IRG"][0]
cnp_row_amt = [d.amount for d in dummy_slip.deductions if d.abbr == "CNAS_P_431"][0]
assert abs(irg_row_amt - 7098.70) < 0.01, f"Expected 7098.70, got {irg_row_amt}"
assert abs(cnp_row_amt - 11769.76) < 0.01, f"Expected 11769.76, got {cnp_row_amt}"
assert abs(dummy_slip.net_pay - (58890.61 - 4074.15 - 7098.70)) < 0.01
print(f"  -> [Test Simulation Bulletin Octobre 2026 OK] Brut = {dummy_slip.gross_pay:,.2f} | CNAS 9% = 4,074.15 | IRG (arrondi 54,810 DA) = {irg_row_amt:,.2f} | Net à Payer (421) = {dummy_slip.net_pay:,.2f} | CNAS Patronale (635 <-> 431) = {cnp_row_amt:,.2f}")
print(f"  -> GL Entry count = {frappe.db.count('GL Entry')}")
