import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HOST = "192.168.100.10"
USER = "frappe"
PASS = "frappe"

REMOTE_SCRIPT = r'''import frappe
from frappe.utils import flt

frappe.init(site='frappe.com')
frappe.connect()

def upsert_child_doctype(name, fields):
    if frappe.db.exists("DocType", name):
        dt = frappe.get_doc("DocType", name)
        dt.fields = []
    else:
        dt = frappe.new_doc("DocType")
        dt.name = name
        dt.module = "Algeria Tax"
        dt.istable = 1
        dt.editable_grid = 1
        dt.engine = "InnoDB"
        dt.custom = 0
    for f in fields:
        dt.append("fields", f)
    dt.save(ignore_permissions=True)
    print(f"Upserted Child DocType: {name} ({len(dt.fields)} fields)")

# 1. Tableau 6 : Acquisitions d'immobilisations (Page 7)
upsert_child_doctype("Bilan Fiscal Tableau 6 Acquisition", [
    {"fieldname": "rubrique_immobilisation", "label": "Rubrique (Nature de l'immobilisation)", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[COMPTE SCF] Désignation de l'immobilisation créée ou acquise (Comptes 203..208, 211, 213, 215, 2181..2184)."},
    {"fieldname": "compte_scf", "label": "Compte SCF", "fieldtype": "Data", "in_list_view": 1, "default": "218",
     "description": "[COMPTE SCF] Numéro du compte d'immobilisation (ex: 215, 2182, 2183)."},
    {"fieldname": "date_acquisition", "label": "Date d'acquisition", "fieldtype": "Date", "in_list_view": 1},
    {"fieldname": "montant_brut", "label": "Montant Brut", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Coût d'acquisition ou de production inscrit au débit du compte de classe 2."},
    {"fieldname": "tva_deduite", "label": "TVA Déduite", "fieldtype": "Currency", "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] TVA récupérable sur immobilisations (Compte 44561)."},
    {"fieldname": "montant_net_a_amortir", "label": "Montant Net à Amortir", "fieldtype": "Currency", "read_only": 1, "in_list_view": 1, "default": 0.0,
     "description": "[FORMULE DGI] = Montant Brut - TVA Déduite (Plafonné à 3 000 000 DZD TTC pour les véhicules de tourisme - Art. 141-2 CIDTA)."}
])

# 2. Tableau 7 : Cessions d'immobilisations (Page 8)
upsert_child_doctype("Bilan Fiscal Tableau 7 Cession", [
    {"fieldname": "nature_immobilisation", "label": "Nature des immobilisations cédées", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[COMPTE SCF] Désignation du bien cédé ou mis au rebut (Comptes 20, 21, 26, 27)."},
    {"fieldname": "compte_scf", "label": "Compte SCF", "fieldtype": "Data", "default": "218"},
    {"fieldname": "date_acquisition", "label": "Date d'acquisition", "fieldtype": "Date", "in_list_view": 1},
    {"fieldname": "date_cession", "label": "Date de cession", "fieldtype": "Date",
     "description": "[RÈGLE CIDTA Art. 172] Détermine le régime de la plus-value : Court terme (<= 3 ans : imposable à 70%) ou Long terme (> 3 ans : imposable à 35%)."},
    {"fieldname": "montant_net_amortir", "label": "Montant net à amortir (V.O)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Valeur d'origine créditée au compte d'immobilisation (Classe 2) lors de la sortie."},
    {"fieldname": "amortissements_pratiques", "label": "Amortissements pratiqués", "fieldtype": "Currency", "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Cumul des amortissements débités au compte 28 lors de la sortie de l'actif."},
    {"fieldname": "valeur_nette_comptable", "label": "Valeur Nette Comptable (VNC)", "fieldtype": "Currency", "read_only": 1, "default": 0.0,
     "description": "[FORMULE DGI] = Montant net à amortir (V.O) - Amortissements pratiqués."},
    {"fieldname": "prix_cession", "label": "Prix de cession", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Prix de vente HT de l'élément cédé (ou 0 en cas de mise au rebut)."},
    {"fieldname": "plus_ou_moins_value", "label": "Plus ou Moins-value", "fieldtype": "Currency", "read_only": 1, "in_list_view": 1, "default": 0.0,
     "description": "[FORMULE DGI] = Prix de cession - (Montant net à amortir - Amortissements pratiqués). Positif = Compte 752 ; Négatif = Compte 652."},
    {"fieldname": "engagement_reinvestissement", "label": "Engagement de réinvestissement (Art. 173 CIDTA)", "fieldtype": "Check", "default": 0,
     "description": "[OPTION FISCALE Art. 173 CIDTA] Exonération à 100% de la plus-value sous engagement de réinvestissement dans un délai de 3 ans."}
])

# 3. Tableau 8/1 : Pertes de valeurs sur créances (Page 9)
upsert_child_doctype("Bilan Fiscal Tableau 8 Creance", [
    {"fieldname": "designation_debiteur", "label": "Désignation des débiteurs (Compte 416)", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[COMPTE SCF] Nom ou raison sociale du client douteux ou litigieux (Compte 416)."},
    {"fieldname": "nif_debiteur", "label": "N.I.F du débiteur", "fieldtype": "Data", "in_list_view": 1},
    {"fieldname": "valeur_creance", "label": "Valeur de la créance (HT)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Montant nominal HT de la créance douteuse (Compte 416)."},
    {"fieldname": "provision_constituee", "label": "Perte de valeur constituée (Compte 491)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Montant de la dépréciation constituée au crédit du compte 491 par le débit du compte 685."},
    {"fieldname": "action_justice_engagee", "label": "Action en justice engagée (Art. 141-5)", "fieldtype": "Check", "in_list_view": 1, "default": 1,
     "description": "[DOCTRINE DGI / ONEC] À défaut de poursuite judiciaire, la dotation au compte 491 est non déductible et doit être réintégrée au Tableau 9 (Ligne 14)."}
])

# 4. Tableau 11 : Participations - Filiales et entités associées (Page 11)
upsert_child_doctype("Bilan Fiscal Tableau 11 Participation", [
    {"fieldname": "filiale_entite", "label": "Filiales et entités associées (Raison sociale & NIF)", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[COMPTE SCF] Identification de la société émettrice des titres (Comptes 261, 262, 265)."},
    {"fieldname": "capitaux_propres_filiale", "label": "Capitaux propres", "fieldtype": "Currency", "in_list_view": 1, "default": 0.0,
     "description": "[INFO FINANCIÈRE] Total des capitaux propres (Total I du Passif) de la filiale ou entité associée."},
    {"fieldname": "quote_part_capital", "label": "Quote-part de capital détenu (%)", "fieldtype": "Percent", "in_list_view": 1, "default": 0.0,
     "description": "[INFO JURIDIQUE] Pourcentage de détention dans le capital social de la filiale."},
    {"fieldname": "resultat_dernier_exercice", "label": "Résultat du dernier exercice", "fieldtype": "Currency", "in_list_view": 1, "default": 0.0,
     "description": "[INFO FINANCIÈRE] Résultat net (Compte 12) du dernier exercice clos de la filiale."},
    {"fieldname": "prets_avances_accordes", "label": "Prêts et avances accordés (266/267)", "fieldtype": "Currency", "default": 0.0,
     "description": "[COMPTE SCF] Solde débiteur des comptes 266 et 267 (Créances rattachées à des participations)."},
    {"fieldname": "dividendes_encaisses", "label": "Dividendes encaissés (Compte 761)", "fieldtype": "Currency", "default": 0.0,
     "description": "[COMPTE SCF] Produits de participations perçus (Compte 761) — déductibles au Tableau 9 Ligne III.3 selon l'Art. 147 bis CIDTA."},
    {"fieldname": "valeur_comptable_titres", "label": "Valeur comptable des titres détenus", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Valeur brute ou nette inscrite aux comptes 261, 262, 265."}
])

# 5. Tableau 12 : Commissions, courtages, redevances, honoraires, sous-traitance (Page 12 - Art. 176 CIDTA)
upsert_child_doctype("Bilan Fiscal Tableau 12 Honoraire", [
    {"fieldname": "designation_beneficiaire", "label": "Désignation des bénéficiaires", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[OBLIGATION Art. 176 CIDTA] Nom, prénom ou raison sociale du bénéficiaire des honoraires, commissions, redevances ou travaux de sous-traitance."},
    {"fieldname": "nature_prestation", "label": "Nature & Compte SCF", "fieldtype": "Select",
     "options": "Honoraires (Compte 622)\nCommissions et courtages (Compte 622)\nSous-traitance générale (Compte 611)\nRedevances brevets et licences (Compte 651)\nRémunérations diverses (Compte 622)",
     "default": "Honoraires (Compte 622)", "in_list_view": 1,
     "description": "[COMPTE SCF] Compte de charge mouvementé (611 Sous-traitance, 622 Honoraires/Commissions, 651 Redevances)."},
    {"fieldname": "nif_beneficiaire", "label": "Identifiant Fiscal (N.I.F)", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[OBLIGATION Art. 176 CIDTA] Numéro d'Identification Fiscale à 15 chiffres du bénéficiaire (obligatoire pour la déductibilité fiscale de la charge)."},
    {"fieldname": "adresse_beneficiaire", "label": "Adresse complète", "fieldtype": "Data", "reqd": 1, "in_list_view": 1,
     "description": "[OBLIGATION Art. 176 CIDTA] Adresse exacte du siège ou domicile professionnel du bénéficiaire."},
    {"fieldname": "montant_percu_ht", "label": "Montant perçu (HT)", "fieldtype": "Currency", "reqd": 1, "in_list_view": 1, "default": 0.0,
     "description": "[COMPTE SCF] Montant HT comptabilisé au débit du compte 611, 622 ou 651 au titre de l'exercice."}
])

frappe.db.commit()
'''

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    sftp = ssh.open_sftp()
    with sftp.open("/home/frappe/create_annex_child_tables.py", "w") as f:
        f.write(REMOTE_SCRIPT)
    sftp.close()

    cmd = "cd /home/frappe/frappe-bench/sites && ../env/bin/python /home/frappe/create_annex_child_tables.py"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode("utf-8", errors="replace"))
    err = stderr.read().decode("utf-8", errors="replace")
    if err:
        print("STDERR:", err)
    ssh.close()

if __name__ == "__main__":
    main()
