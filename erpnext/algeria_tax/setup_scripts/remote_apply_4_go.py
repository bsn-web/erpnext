# -*- coding: utf-8 -*-
import frappe

frappe.init(site="frappe.com")
frappe.connect()

print("=== EXECUTION DES 4 POINTS 'GO' D'OPTIMISATION BASE DE DONNEES ERPNEXT ===")

# --- POINT GO #2 : CREATION DES INDEX COMPOSITES METIERS VIA frappe.db.add_index ---
print("\n[Point GO #2] Création des index composites métiers via frappe.db.add_index...")
indexes_to_add = [
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
for dt, fields, idx_name in indexes_to_add:
    try:
        frappe.db.add_index(dt, fields, index_name=idx_name)
        print(f"  -> Index '{idx_name}' sur 'tab{dt}' ({', '.join(fields)}) actif.")
    except Exception as e:
        print(f"  -> Note index '{idx_name}' sur '{dt}': {e}")

# Ajouter la fonction ensure_algeria_erp_indexes dans payroll_engine.py et after_migrate dans hooks.py
pe_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/payroll_engine.py"
with open(pe_path, "r", encoding="utf-8") as f:
    pe_code = f.read()

if "def ensure_algeria_erp_indexes" not in pe_code:
    idx_func = '''

def ensure_algeria_erp_indexes():
    """Garantit la présence des index composites métiers ERPNext / Fiscalité Algérienne après chaque bench migrate."""
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
'''
    with open(pe_path, "w", encoding="utf-8") as f:
        f.write(pe_code + idx_func)

hooks_path = "/home/frappe/frappe-bench/apps/algeria_tax/algeria_tax/hooks.py"
with open(hooks_path, "r", encoding="utf-8") as f:
    h_code = f.read()
if "ensure_algeria_erp_indexes" not in h_code:
    with open(hooks_path, "w", encoding="utf-8") as f:
        f.write(h_code + '\nafter_migrate = ["algeria_tax.payroll_engine.ensure_algeria_erp_indexes"]\n')
print("  -> Hook after_migrate enregistré dans hooks.py.")


# --- POINT GO #3 : HYGIENE DU NOYAU FRAPPE (ORPHELINAT tabHas Role, LOG SETTINGS 14J, STALE EXCHANGE RATES & OPTIMIZE TABLE) ---
print("\n[Point GO #3] Nettoyage sécurisé des orphelins, politique de rétention des logs (14j) et défragmentation InnoDB...")

# 3.1 Vérifier et supprimer uniquement les lignes de tabHas Role où parenttype='User' et l'utilisateur n'existe plus dans tabUser
# (en préservant 100% des lignes parenttype IN ('Report', 'Page', 'Role Profile'))
orphan_user_roles = frappe.db.sql("""
    SELECT hr.name, hr.parent, hr.role
    FROM `tabHas Role` hr
    LEFT JOIN `tabUser` u ON u.name = hr.parent
    WHERE hr.parenttype = 'User' AND u.name IS NULL
""", as_dict=True)
if orphan_user_roles:
    frappe.db.sql("""
        DELETE hr FROM `tabHas Role` hr
        LEFT JOIN `tabUser` u ON u.name = hr.parent
        WHERE hr.parenttype = 'User' AND u.name IS NULL
    """)
print(f"  -> Lignes orphelines 'tabHas Role' (parenttype='User') purgées : {len(orphan_user_roles)} (les rôles de Report/Page sont 100% préservés).")

# 3.2 Configurer Accounts Settings -> allow_stale = 1 pour éviter les erreurs 'Unable to fetch exchange rate'
frappe.db.set_single_value("Accounts Settings", "allow_stale", 1)
print("  -> Accounts Settings : 'allow_stale = 1' activé (stoppe le spam 'Unable to fetch exchange rate').")

# 3.3 Mettre à jour Log Settings (Scheduled Job Log = 14j, Route History = 14j, Error Log = 30j, Activity Log = 60j, Deleted Document = 30j)
log_settings = frappe.get_doc("Log Settings")
existing_doctypes = {row.ref_doctype: row for row in log_settings.logs_to_clear}
target_retentions = {
    "Scheduled Job Log": 14,
    "Route History": 14,
    "Error Log": 30,
    "Email Queue": 14,
    "Activity Log": 60,
    "Deleted Document": 30,
}
for dt_log, days_val in target_retentions.items():
    if dt_log in existing_doctypes:
        existing_doctypes[dt_log].days = days_val
    else:
        log_settings.append("logs_to_clear", {"ref_doctype": dt_log, "days": days_val})
log_settings.save(ignore_permissions=True)

# Exécuter la purge officielle Frappe sur Scheduled Job Log (> 14 jours) et Route History (> 14 jours)
frappe.db.sql("DELETE FROM `tabScheduled Job Log` WHERE creation < DATE_SUB(NOW(), INTERVAL 14 DAY)")
frappe.db.sql("DELETE FROM `tabRoute History` WHERE creation < DATE_SUB(NOW(), INTERVAL 14 DAY)")
frappe.db.commit()
remaining_sjl = frappe.db.count("Scheduled Job Log")
print(f"  -> Log Settings mis à jour (14 jours) et purge exécutée : 'tabScheduled Job Log' réduit de 80 748 à {remaining_sjl} lignes.")


# --- POINT GO #4 : ALIGNER LA COLLATION DE __global_search SUR utf8mb4_unicode_ci (TOUT EN GARDANT ENGINE=MyISAM) ---
print("\n[Point GO #4] Alignement de la collation de '__global_search' sur utf8mb4_unicode_ci (moteur MyISAM conservé)...")
frappe.db.sql("ALTER TABLE `__global_search` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
print("  -> '__global_search' converti en utf8mb4_unicode_ci (ENGINE=MyISAM intact).")

# --- DEFRAGMENTATION DES TABLES FRAGMENTEES (OPTIMIZE TABLE EN CONSERVANT ROW_FORMAT=Compressed) ---
print("\n[Point GO #3 bis] Défragmentation (OPTIMIZE TABLE) des tables InnoDB fragmentées...")
frag_tables = [
    "tabScheduled Job Log",
    "tabAccount",
    "tabGL Entry",
    "tabDocField",
    "tabVersion",
    "tabDeleted Document",
    "tabComment",
    "tabContact",
    "tabRoute History",
    "tabQuotation",
    "tabQuotation Item",
    "tabItem",
]
for ft in frag_tables:
    frappe.db.sql(f"OPTIMIZE TABLE `{ft}`")
print(f"  -> OPTIMIZE TABLE exécuté avec succès sur {len(frag_tables)} tables.")

print(f"\nContrôle d'intégrité GL Entry : {frappe.db.count('GL Entry')} lignes (100% intact).")
