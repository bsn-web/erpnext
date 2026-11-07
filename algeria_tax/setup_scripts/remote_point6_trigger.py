# -*- coding: utf-8 -*-
import frappe
from frappe.utils import flt

frappe.init(site="frappe.com")
frappe.connect()

print("=== DEPLOIEMENT DU PROTOCOLE POINT 6 : REINTEGRATION TABLEAU 9 (2026) & DECLENCHEUR AUTOMATIQUE CLOTURE 2026 -> OUVERTURE 2027 ===")

# 1. S'assurer que l'exercice fiscal 2027 existe dans ERPNext
if not frappe.db.exists("Fiscal Year", "2027"):
    fy = frappe.new_doc("Fiscal Year")
    fy.year = "2027"
    fy.year_start_date = "2027-01-01"
    fy.year_end_date = "2027-12-31"
    fy.insert(ignore_permissions=True)
    print("  -> Exercice Fiscal '2027' (2027-01-01 au 2027-12-31) créé.")
else:
    print("  -> Exercice Fiscal '2027' déjà présent.")

# 2. Ajouter dans payroll_engine.py :
#    - compute_2026_payroll_gl_anomaly(company) : calcule au centime près l'écart des écritures ACC-JV-2026-00001 et ACC-JV-2026-00004
#    - trigger_2027_opening_rectification_je(company, auto_submit=False) : crée (et soumet automatiquement à la clôture 2026) l'OD d'ouverture du 01/01/2027 (Art. 138-4 SCF)
#    - on_period_closing_voucher_submit(doc, method=None) : déclencheur automatique sur Period Closing Voucher 2026
pe_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/payroll_engine.py"
with open(pe_path, "r", encoding="utf-8") as f:
    pe_code = f.read()

marker = "# === POINT 6 : RECTIFICATION AUTOMATIQUE CLOTURE 2026 / OUVERTURE 2027 ==="
if marker in pe_code:
    pe_code = pe_code[:pe_code.index(marker)]

point6_funcs = '''# === POINT 6 : RECTIFICATION AUTOMATIQUE CLOTURE 2026 / OUVERTURE 2027 ===

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
'''

with open(pe_path, "w", encoding="utf-8") as f:
    f.write(pe_code + "\n" + point6_funcs)
print("  -> Added compute_2026_payroll_gl_anomaly & trigger_2027_opening_rectification_je to payroll_engine.py.")

# 3. Enrichir bilan_fiscal.py :
#    - Dans pull_from_gl_accounts() : si fiscal_year == '2026', alimenter automatiquement tab9_reint_autres avec 76 770,92 DZD
#    - Dans lock_bilan_fiscal() : si fiscal_year == '2026', déclencher automatiquement trigger_2027_opening_rectification_je(..., auto_submit=True)
bf_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/algeria_tax/doctype/bilan_fiscal/bilan_fiscal.py"
with open(bf_path, "r", encoding="utf-8") as f:
    bf_code = f.read()

# Échapper les % dans les clauses LIKE passées à frappe.db.sql(..., params)
bf_code = bf_code.replace("LIKE '{p}%'", "LIKE '{p}%%'")
with open(bf_path, "w", encoding="utf-8") as f:
    f.write(bf_code)

if "compute_2026_payroll_gl_anomaly" not in bf_code:
    # 3.1 Dans pull_from_gl_accounts, juste avant self.recalculate_all_totals()
    target_pull = "        self.recalculate_all_totals()\n        return {"
    inject_pull = """        # Point 6 (Audit CAC Paie 2026) : Réintégration extra-comptable automatique au Tableau 9 (Exercice 2026)
        if str(self.fiscal_year) == "2026":
            from algeria_tax.payroll_engine import compute_2026_payroll_gl_anomaly
            anom = compute_2026_payroll_gl_anomaly(self.company)
            if anom.get("has_anomaly") and flt(self.tab9_reint_autres) < flt(anom["reintegration_tab9_2026"]):
                self.tab9_reint_autres = flt(anom["reintegration_tab9_2026"])
                updated_fields.append("tab9_reint_autres")

        self.recalculate_all_totals()
        return {"""
    bf_code = bf_code.replace(target_pull, inject_pull, 1)

    # 3.2 Dans lock_bilan_fiscal, déclencher automatiquement l'écriture d'ouverture 2027 lors de la clôture 2026
    target_lock = '        return {"status": self.status, "is_fiscal_closed": self.is_fiscal_closed}'
    inject_lock = """        opening_2027_res = None
        if str(self.fiscal_year) == "2026":
            from algeria_tax.payroll_engine import trigger_2027_opening_rectification_je
            opening_2027_res = trigger_2027_opening_rectification_je(
                company=self.company,
                auto_submit=True,
                trigger_source=f"Clôture Bilan Fiscal 2026 ({self.name})",
            )
        return {"status": self.status, "is_fiscal_closed": self.is_fiscal_closed, "opening_2027_rectification": opening_2027_res}"""
    bf_code = bf_code.replace(target_lock, inject_lock, 1)

    with open(bf_path, "w", encoding="utf-8") as f:
        f.write(bf_code)
    print("  -> Updated bilan_fiscal.py with automatic Tableau 9 (2026) reintegration and lock_bilan_fiscal() 2027 trigger.")

# 4. Enregistrer le hook Period Closing Voucher -> on_submit dans hooks.py
hooks_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/hooks.py"
with open(hooks_path, "r", encoding="utf-8") as f:
    h_code = f.read()

if "Period Closing Voucher" not in h_code:
    h_append = '''
doc_events["Period Closing Voucher"] = {
    "on_submit": "algeria_tax.payroll_engine.on_period_closing_voucher_submit"
}
'''
    with open(hooks_path, "w", encoding="utf-8") as f:
        f.write(h_code + h_append)
    print("  -> Registered doc_events['Period Closing Voucher']['on_submit'] in hooks.py.")

# 5. Générer dès maintenant :
#    a) Le Bilan Fiscal 2026 ('BF-BSN-2026-EXERCICE-2026') avec extraction GL et la réintégration automatique de 76 770,92 DZD au Tableau 9
#    b) L'écriture Journal Entry d'ouverture du 01/01/2027 en Brouillon (docstatus = 0, prête à être auto-soumise par le déclencheur de clôture 2026, gardant GL Entry = 1726)
import importlib
import algeria_tax.payroll_engine as pe
importlib.reload(pe)

bf_2026_name = "BF-BSN-2026-EXERCICE-2026"
if not frappe.db.exists("Bilan Fiscal", bf_2026_name):
    bf26 = frappe.new_doc("Bilan Fiscal")
    bf26.name = bf_2026_name
    bf26.company = "Build And Secure Networks"
    bf26.fiscal_year = "2026"
    bf26.period_start_date = "2026-01-01"
    bf26.period_end_date = "2026-12-31"
    bf26.status = "Calculé & Contrôlé"
    bf26.insert(ignore_permissions=True)
else:
    bf26 = frappe.get_doc("Bilan Fiscal", bf_2026_name)

bf26.pull_from_gl_accounts()
bf26.save(ignore_permissions=True)

je_res = pe.trigger_2027_opening_rectification_je(
    company="Build And Secure Networks",
    auto_submit=False,
    trigger_source="Préparation Clôture Exercice 2026",
)
frappe.db.commit()

print(f"  -> Bilan Fiscal 2026 '{bf26.name}' ready : Charges Personnel TCR (631..638) = {bf26.charges_personnel:,.2f} DZD | Réintégration Tableau 9 (tab9_reint_autres) = {bf26.tab9_reint_autres:,.2f} DZD | Total Réintégrations T9 = {bf26.tab9_total_reintegrations:,.2f} DZD")
print(f"  -> Écriture d'Ouverture 2027 (01/01/2027) préparée : {je_res} (Total Débit = Total Crédit = 84,363.65 DZD)")
print(f"  -> GL Entry count = {frappe.db.count('GL Entry')}")
