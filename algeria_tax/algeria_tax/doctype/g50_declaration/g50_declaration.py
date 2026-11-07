# -*- coding: utf-8 -*-
# Copyright (c) 2026, Algeria Tax & SCF Compliance
# Référentiel Officiel : Série G n° 50 (DGI / Jibayatic), CIDTA, CTCA (Art. 14, 21, 23, 29, 30, 224), Code du Timbre & LF 2024-2026

import calendar
import frappe
from frappe.model.document import Document
from frappe.utils import flt

# Mots-clés et codes identifiant une ligne de Prestation de Service / Travaux (Art. 14-2 CTCA : Fait générateur = Encaissement)
SERVICE_ITEM_KEYWORDS = (
    "monthly support", "hebergement", "hébergement", "configuration", "configuraion",
    "confi-all", "maintenance", "reparation", "réparation", "repair", "cabling work",
    "installation", "déploiement", "deploiement", "mise en service", "formation",
    "implimentation", "implementation", "service et programmation", "prestation",
    "troubleshooting", "moving costs", "montage du matériel", "connexion internet",
    "creation site web", "création site web", "erp01", "erp02", "exch2016",
)

SERVICE_ITEM_CODES = {
    "ERP01", "ERP02", "SI", "confi-all", "Configuration", "exch2016",
    "Maintenance", "fix", "Repair", "CAb", "TNS-09", "Montage",
}


def is_service_invoice_line(row):
    """
    Détermine si une ligne de Sales Invoice Item relève de la 'Prestation de service / Travaux' (True)
    ou de la 'Vente en l'état / Livraison de biens' (False).
    """
    grp = (row.get("item_group") or "").strip().lower()
    if grp in ("services", "prestations de services", "travaux") or "service" in grp or "prestation" in grp:
        return True
    acct = (row.get("income_account") or "").strip()
    if acct.startswith(("704", "705", "706")):
        return True
    code = (row.get("item_code") or "").strip()
    if code in SERVICE_ITEM_CODES:
        return True
    text = f"{code} {row.get('item_name') or ''}".lower()
    for kw in SERVICE_ITEM_KEYWORDS:
        if kw in text:
            return True
    return False


def classify_sales_invoice(si_name):
    """
    Analyse toutes les lignes d'une facture de vente (Sales Invoice) et applique la règle de prépondérance (> 50% du TTC) :
    - Si la somme TTC des lignes 'Prestation de service' représente > 50% du TTC de la facture :
      => Type majoritaire = 'Prestation de service (Encaissement - Art. 14-2 CTCA)' (TVA exigible sur Payment Entry)
    - Si la somme TTC des lignes 'Vente en l'état' représente >= 50% du TTC de la facture :
      => Type majoritaire = 'Vente en l'état (Facturation - Art. 14-1 CTCA)' (TVA exigible à la facturation)
    """
    si = frappe.db.sql("""
        SELECT si.name, si.posting_date, si.customer, si.customer_name, si.tax_id,
               si.base_net_total, si.base_total_taxes_and_charges, si.base_grand_total,
               si.outstanding_amount, si.is_pos, c.tax_id as cust_tax_id
        FROM `tabSales Invoice` si
        LEFT JOIN `tabCustomer` c ON c.name = si.customer
        WHERE si.name = %s
    """, (si_name,), as_dict=True)
    if not si:
        return None
    si = si[0]

    rows = frappe.db.sql("""
        SELECT item_code, item_name, description, item_group, income_account, base_net_amount, base_amount
        FROM `tabSales Invoice Item`
        WHERE parent = %s
    """, (si_name,), as_dict=True)

    ttc_factor = (flt(si.base_grand_total) / flt(si.base_net_total)) if flt(si.base_net_total) != 0 else 1.19
    service_ttc = 0.0
    bien_ttc = 0.0

    for r in rows:
        line_ht = flt(r.base_net_amount or r.base_amount or 0.0)
        line_ttc = line_ht * ttc_factor
        if is_service_invoice_line(r):
            service_ttc += line_ttc
        else:
            bien_ttc += line_ttc

    denom = abs(service_ttc) + abs(bien_ttc)
    if denom > 0.001:
        service_ratio = abs(service_ttc) / denom
    else:
        service_ratio = 0.0

    service_pct = round(service_ratio * 100.0, 2)
    bien_pct = round(100.0 - service_pct, 2)
    is_mixed = (abs(service_ttc) > 0.001 and abs(bien_ttc) > 0.001)
    # Règle stricte demandée : Sélectionner le type qui a un montant > 50% du TTC
    is_majority_service = (service_ratio > 0.50)

    return {
        "si": si,
        "service_ttc": service_ttc,
        "bien_ttc": bien_ttc,
        "service_pct": service_pct,
        "bien_pct": bien_pct,
        "is_mixed": is_mixed,
        "is_majority_service": is_majority_service,
        "type_operation": (
            "Prestation de service (Encaissement - Art. 14-2 CTCA)"
            if is_majority_service
            else "Vente en l'état (Facturation - Art. 14-1 CTCA)"
        ),
    }


class G50Declaration(Document):
    def validate(self):
        # 1. Contrôle de verrouillage après dépôt Jibayatic ou clôture de l'exercice fiscal
        if not self.is_new():
            was_locked = frappe.db.get_value("G50 Declaration", self.name, "is_g50_locked")
            was_status = frappe.db.get_value("G50 Declaration", self.name, "status")
            if (was_locked or was_status == "Déposé Jibayatic") and not getattr(self.flags, "in_lock_action", False):
                frappe.throw(
                    "🔒 <b>Déclaration G50 Verrouillée (Lecture Seule)</b> : "
                    "Cette déclaration mensuelle Série G n° 50 a déjà été télé-déclarée / clôturée. "
                    "Aucune modification n'est autorisée (toute régularisation doit faire l'objet d'une G50 complémentaire).",
                    frappe.ValidationError,
                )

        # Vérifier si l'exercice fiscal est clôturé dans Bilan Fiscal ou Period Closing Voucher
        if self.fiscal_year and self.company:
            bf_closed = frappe.db.exists(
                "Bilan Fiscal",
                {"company": self.company, "fiscal_year": self.fiscal_year, "is_fiscal_closed": 1},
            )
            pcv_closed = frappe.db.exists(
                "Period Closing Voucher",
                {"company": self.company, "fiscal_year": self.fiscal_year, "docstatus": 1},
            )
            if bf_closed or pcv_closed:
                self.is_g50_locked = 1

        # 2. Calcul intégral de toutes les formules officielles DGI / CTCA / CIDTA
        self.recalculate_all_g50()

    @frappe.whitelist()
    def recalculate_all_g50(self):
        """Calcule l'intégralité des cases [FORMULE DGI] sur les 5 paragraphes et les 2 annexes de la G50."""
        # --- DATE LIMITE LÉGALE (20 du mois M+1 - Art. 355 CIDTA & Art. 76 CTCA) ---
        try:
            m_num = int((self.declaration_month or "11").split("-")[0].strip())
            yr = int(self.fiscal_year or 2026)
            if m_num == 12:
                self.due_date_legale = f"{yr + 1}-01-20"
            else:
                self.due_date_legale = f"{yr}-{m_num + 1:02d}-20"
        except Exception:
            self.due_date_legale = "2026-12-20"

        # --- ANNEXE 1 : ÉTAT DÉTAILLÉ DES FOURNISSEURS / DÉDUCTIONS TVA (Art. 29 & 30 CTCA) ---
        total_af_ht = 0.0
        total_af_biens = 0.0
        total_af_immos = 0.0
        for row in (self.get("annexe_fournisseurs") or []):
            ht = flt(row.montant_ht)
            taux = flt(row.taux_tva or 19.0)
            # Préserver la TVA exacte de la facture si elle correspond à moins d'1 DZD d'écart d'arrondi
            existing_tva = flt(row.montant_tva_deduite)
            calc_tva = round(ht * taux / 100.0, 2)
            tva_brute = existing_tva if (existing_tva > 0 and abs(existing_tva - calc_tva) <= 1.0) else round(ht * taux / 100.0)
            row.montant_ttc = round(ht + tva_brute, 2)
            # Application stricte de l'Article 30 du CTCA : exclusion du droit à déduction si espèces > 1 000 000 DZD TTC
            mode = row.mode_paiement or ""
            if "Espèces" in mode and (row.montant_ttc > 1000000.0 or "> 1 000 000" in mode):
                row.montant_tva_deduite = 0.0
            else:
                row.montant_tva_deduite = tva_brute

            total_af_ht = round(total_af_ht + ht, 2)
            if "Immobilisations" in (row.nature_achat or ""):
                total_af_immos = round(total_af_immos + row.montant_tva_deduite, 2)
            else:
                total_af_biens = round(total_af_biens + row.montant_tva_deduite, 2)

        self.annexe_fournisseurs_total_ht = total_af_ht
        self.annexe_fournisseurs_total_tva_biens = total_af_biens
        self.annexe_fournisseurs_total_tva_immos = total_af_immos
        self.annexe_fournisseurs_total_tva = round(total_af_biens + total_af_immos, 2)

        if self.sync_tva_from_annexe_fournisseurs and (self.get("annexe_fournisseurs") or []):
            self.tva_deductible_goods = self.annexe_fournisseurs_total_tva_biens
            self.tva_deductible_assets = self.annexe_fournisseurs_total_tva_immos

        # --- ANNEXE 2 : ÉTAT DÉTAILLÉ DES CLIENTS (Art. 14 & 224 CTCA) ---
        total_ac_ht = 0.0
        total_ac_tva = 0.0
        total_ac_ttc = 0.0
        vent_etat_ht = 0.0
        vent_etat_tva = 0.0
        prest_enc_ht = 0.0
        prest_enc_tva = 0.0

        for row in (self.get("annexe_clients") or []):
            ht = round(flt(row.montant_ht), 2)
            reg = row.regime_tva_vente or ""
            if "19%" in reg:
                calc_tva = round(ht * 0.19, 2)
                row.montant_tva = flt(row.montant_tva) if (flt(row.montant_tva) != 0 and abs(flt(row.montant_tva) - calc_tva) <= 1.0) else calc_tva
            elif "9%" in reg:
                calc_tva = round(ht * 0.09, 2)
                row.montant_tva = flt(row.montant_tva) if (flt(row.montant_tva) != 0 and abs(flt(row.montant_tva) - calc_tva) <= 1.0) else calc_tva
            else:
                row.montant_tva = 0.0
            row.montant_ttc = round(ht + row.montant_tva, 2)

            total_ac_ht = round(total_ac_ht + ht, 2)
            total_ac_tva = round(total_ac_tva + row.montant_tva, 2)
            total_ac_ttc = round(total_ac_ttc + row.montant_ttc, 2)

            if "Prestation" in (row.type_operation or "") or row.payment_entry_ref:
                prest_enc_ht = round(prest_enc_ht + ht, 2)
                prest_enc_tva = round(prest_enc_tva + row.montant_tva, 2)
            else:
                vent_etat_ht = round(vent_etat_ht + ht, 2)
                vent_etat_tva = round(vent_etat_tva + row.montant_tva, 2)

        self.annexe_clients_total_ht = total_ac_ht
        self.annexe_clients_total_tva = total_ac_tva
        self.annexe_clients_total_ttc = total_ac_ttc

        if self.get("annexe_clients"):
            self.ca_vente_etat_ht_mois = vent_etat_ht
            self.tva_vente_etat_mois = vent_etat_tva
            self.ca_prestation_encaisse_ht_mois = prest_enc_ht
            self.tva_prestation_encaisse_mois = prest_enc_tva

        # --- PARAGRAPHE 5 : TAXES SUR LE CHIFFRE D'AFFAIRES / TVA (E4 & Cadres A, B, C, E, P) ---
        self.tva_collectee_19 = round(flt(self.ca_taxable_19) * 0.19, 2)
        self.tva_collectee_9 = round(flt(self.ca_taxable_9) * 0.09, 2)
        self.tva_autoliquidation_19 = round(flt(self.ca_autoliquidation_services_importes) * 0.19, 2)

        self.ca_total_ht_mois = round(
            flt(self.ca_taxable_19)
            + flt(self.ca_taxable_9)
            + flt(self.ca_exportation_exonere)
            + flt(self.ca_exonere_franchise),
            2,
        )

        self.total_tva_collectee = round(
            flt(self.tva_collectee_19)
            + flt(self.tva_collectee_9)
            + flt(self.tva_regularisation_reprise)
            + flt(self.tva_autoliquidation_19),
            2,
        )

        self.total_tva_deductible = round(
            flt(self.tva_credit_reporte_anterior)
            + flt(self.tva_deductible_goods)
            + flt(self.tva_deductible_assets)
            + flt(self.tva_deductible_complementaire),
            2,
        )

        self.tva_nette_a_payer = round(max(0.0, self.total_tva_collectee - self.total_tva_deductible), 2)
        self.tva_nouveau_credit = round(max(0.0, self.total_tva_deductible - self.total_tva_collectee), 2)

        # --- PARAGRAPHE 1 : TAP (Abrogée Art. 14 LF 2024) / TLS (Codes C1A11..C1A14) ---
        if flt(self.c1a11_ca_brut_mois) == 0.0 and self.ca_total_ht_mois > 0.0:
            self.c1a11_ca_brut_mois = self.ca_total_ht_mois
        if flt(self.c1a14_taux_tls) == 0.0:
            self.c1a12_operations_exonerees = flt(self.c1a11_ca_brut_mois)
        self.c1a13_ca_imposable_tls = max(0.0, flt(self.c1a11_ca_brut_mois) - flt(self.c1a12_operations_exonerees))
        self.tap_tls_droits_dus = round(self.c1a13_ca_imposable_tls * flt(self.c1a14_taux_tls) / 100.0)

        # --- PARAGRAPHE 2 : ACOMPTES PROVISIONNELS & SOLDE IBS / IRG (E1M10, E1M20, E1M30) ---
        # Gestion complète des Avantages Fiscaux (AAPI, NESDA/ANADE, CNAC, ANGEM, Startup, Grand Sud Art. 138 bis, Export, Taux réduit 10%)
        disp = self.e1m10_dispositif_avantage or "Aucun (Régime de droit commun)"
        if "100%" in disp:
            self.e1m10_taux_abattement_exo = 100.0
        elif "70%" in disp:
            self.e1m10_taux_abattement_exo = 70.0
        elif "50%" in disp:
            self.e1m10_taux_abattement_exo = 50.0
        elif "25%" in disp:
            self.e1m10_taux_abattement_exo = 25.0
        elif "Taux Réduit IBS 10%" in disp:
            self.e1m10_taux_ibs_applicable = 10.0
            self.e1m10_taux_abattement_exo = 0.0
        elif "Aucun" in disp:
            self.e1m10_taux_abattement_exo = 0.0

        taux_ibs = flt(self.e1m10_taux_ibs_applicable or 26.0)
        taux_abatt = min(100.0, max(0.0, flt(self.e1m10_taux_abattement_exo)))

        if flt(self.e1m10_base_benefice_ref) > 0.0:
            self.e1m10_ibs_brut_avant_avantage = round(flt(self.e1m10_base_benefice_ref) * taux_ibs / 100.0)
            self.e1m10_montant_avantage_ibs = round(self.e1m10_ibs_brut_avant_avantage * taux_abatt / 100.0)
            ibs_net_apres_avantage = max(0.0, self.e1m10_ibs_brut_avant_avantage - self.e1m10_montant_avantage_ibs)
            if taux_abatt >= 100.0:
                # Exonération totale (100%) : dispense intégrale d'acomptes IBS et du minimum forfaitaire de 10 000 DZD
                self.e1m10_ibs_reference = 0.0
            else:
                self.e1m10_ibs_reference = max(10000.0, ibs_net_apres_avantage)
        else:
            self.e1m10_ibs_brut_avant_avantage = 0.0
            self.e1m10_montant_avantage_ibs = 0.0
            self.e1m10_ibs_reference = 0.0

        if self.e1m10_numero_acompte and "Aucun" not in self.e1m10_numero_acompte:
            acompte_brut_30 = round(self.e1m10_ibs_reference * 0.30)
            self.e1m10_acompte_ibs_droits = max(
                0.0, acompte_brut_30 - round(flt(self.e1m10_imputation_excedent_anterieur))
            )
        else:
            self.e1m10_acompte_ibs_droits = 0.0

        self.e1m20_solde_ibs_droits = max(0.0, flt(self.e1m20_ibs_annuel_liquide) - flt(self.e1m20_total_acomptes_verses))
        self.e1m20_excedent_ibs_a_imputer = max(
            0.0, flt(self.e1m20_total_acomptes_verses) - flt(self.e1m20_ibs_annuel_liquide)
        )

        # --- PARAGRAPHE 3 : IRG SALAIRES & RETENUES À LA SOURCE (E2M05 à E2M40) ---
        if flt(self.base_dividendes_distribues) > 0.0:
            self.irg_dividendes_15 = round(flt(self.base_dividendes_distribues) * 0.15)
        self.irg_interets_creances_10 = round(flt(self.base_interets_creances) * 0.10)
        if flt(self.base_irg_honoraires) > 0.0 and flt(self.irg_honoraires_10) == 0.0:
            self.irg_honoraires_10 = round(flt(self.base_irg_honoraires) * 0.10)
        self.ibs_retenue_etranger_30 = round(flt(self.base_ibs_etranger_30) * 0.30)

        # --- RÉCAPITULATION GÉNÉRALE (1 à 5 + PÉNALITÉS) ---
        self.recap_p1_tap_tls = flt(self.tap_tls_droits_dus)
        self.recap_p2_acomptes_ibs_irg = (
            flt(self.e1m10_acompte_ibs_droits)
            + flt(self.e1m20_solde_ibs_droits)
            + flt(self.e1m30_acompte_irg_droits)
        )
        self.recap_p3_irg_retenues = (
            flt(self.irg_salaries_retenu)
            + flt(self.irg_dividendes_15)
            + flt(self.irg_interets_creances_10)
            + flt(self.irg_honoraires_10)
            + flt(self.ibs_retenue_etranger_30)
        )
        self.recap_p4_timbre_autres = (
            flt(self.droit_de_timbre_especes)
            + flt(self.taxe_formation_apprentissage)
            + flt(self.autres_taxes_paragraphe_4)
        )
        self.recap_p5_tva_a_payer = flt(self.tva_nette_a_payer)

        sous_total = round(
            self.recap_p1_tap_tls
            + self.recap_p2_acomptes_ibs_irg
            + self.recap_p3_irg_retenues
            + self.recap_p4_timbre_autres
            + self.recap_p5_tva_a_payer,
            2,
        )
        self.penalite_retard_montant = round(sous_total * flt(self.penalite_retard_taux) / 100.0, 2)
        self.total_g50_a_payer = round(sous_total + self.penalite_retard_montant, 2)

        # --- CONTRÔLES CAC / EXPERT-COMPTABLE ---
        self.ecart_ca_tva_collectee = round(
            (flt(self.tva_collectee_19) - round(flt(self.ca_taxable_19) * 0.19, 2))
            + (flt(self.tva_collectee_9) - round(flt(self.ca_taxable_9) * 0.09, 2)),
            2,
        )
        if self.get("annexe_fournisseurs"):
            self.ecart_tva_deductible_annexe = round(
                (flt(self.tva_deductible_goods) + flt(self.tva_deductible_assets))
                - flt(self.annexe_fournisseurs_total_tva),
                2,
            )
        else:
            self.ecart_tva_deductible_annexe = 0.0

        if self.get("annexe_clients"):
            self.ecart_ca_annexe_clients = round(flt(self.ca_total_ht_mois) - flt(self.annexe_clients_total_ht), 2)
        else:
            self.ecart_ca_annexe_clients = 0.0

        # --- GÉNÉRATION AUTOMATIQUE DU TABLEAU SYNTHÉTIQUE DES LIGNES G50 ---
        self.rebuild_official_tax_lines()

        return {
            "total_tva_collectee": self.total_tva_collectee,
            "total_tva_deductible": self.total_tva_deductible,
            "tva_nette_a_payer": self.tva_nette_a_payer,
            "tva_nouveau_credit": self.tva_nouveau_credit,
            "total_g50_a_payer": self.total_g50_a_payer,
        }

    def rebuild_official_tax_lines(self):
        self.tax_lines = []
        lines_spec = [
            ("C1A11", "TAP / TLS (Abrogée droit commun Art. 14 LF 2024)", "1. TAP / TLS (C1)", "[COMPTE SCF 70 / 447] Formule: CA Imposable * Taux TLS", self.c1a13_ca_imposable_tls, self.c1a14_taux_tls, self.tap_tls_droits_dus),
            ("E1M10", f"Acompte Provisionnel IBS ({self.e1m10_numero_acompte or '30%'})", "2. Acomptes & Solde IBS/IRG (E1)", "[COMPTE SCF 4441 SD] Formule: IBS Réf N-1 * 30% (Art. 356 CIDTA)", self.e1m10_ibs_reference, 30.0 if self.e1m10_acompte_ibs_droits > 0 else 0.0, self.e1m10_acompte_ibs_droits),
            ("E1M20", "Solde de Liquidation IBS", "2. Acomptes & Solde IBS/IRG (E1)", "[COMPTE SCF 444 SC] Formule: max(0, IBS liquidé - Acomptes versés)", self.e1m20_ibs_annuel_liquide, 100.0, self.e1m20_solde_ibs_droits),
            ("E2M05", "IRG / Traitements et Salaires", "3. IRG Salaires & Retenues (E2)", "[COMPTE SCF 4421 SC] Barème progressif IRG (Exonéré <= 30 000 DZD)", self.masse_salariale_imposable, 0.0, self.irg_salaries_retenu),
            ("E2M10", "IRG / Revenus des Capitaux Mobiliers (Dividendes)", "3. IRG Salaires & Retenues (E2)", "[COMPTE SCF 4422 SC] Formule: Base Dividendes (457) * 15% (Art. 104 CIDTA)", self.base_dividendes_distribues, 15.0, self.irg_dividendes_15),
            ("E2M30", "IRG / Honoraires et Autres Retenues à la Source", "3. IRG Salaires & Retenues (E2)", "[COMPTE SCF 4423 SC] Retenue à la source 10%", self.base_irg_honoraires, 10.0, self.irg_honoraires_10),
            ("E2M40", "IBS / Retenue à la Source Entreprises Étrangères (30%)", "3. IRG Salaires & Retenues (E2)", "[COMPTE SCF 4423 SC] Formule: Contrat Services Étrangers * 30% (Art. 156 CIDTA)", self.base_ibs_etranger_30, 30.0, self.ibs_retenue_etranger_30),
            ("E3L10", "Droits de Timbre sur État (Quittances Espèces)", "4. Timbre & Autres Taxes (E3)", "[COMPTE SCF 4458 / 447 SC] 1% à 2% sur encaissements espèces (531)", self.base_encaissements_especes, 1.0, self.droit_de_timbre_especes),
            ("E4L01", f"TVA Collectée 19% (Ventes état: {flt(self.ca_vente_etat_ht_mois):,.0f} HT | Prestations encaissées: {flt(self.ca_prestation_encaisse_ht_mois):,.0f} HT)", "5. TVA Collectée (E4 - A)", "[COMPTE SCF 44571 SC & ART. 14 CTCA] Facturation (Biens >=50% TTC) + Encaissement Payment Entry (Services >50% TTC)", self.ca_taxable_19, 19.0, self.tva_collectee_19),
            ("E4L02", "TVA Collectée au Taux Réduit de 9%", "5. TVA Collectée (E4 - A)", "[COMPTE SCF 44572 SC] Formule: CA Taxable 9% (70) * 9% (Art. 23 CTCA)", self.ca_taxable_9, 9.0, self.tva_collectee_9),
            ("E4L11", "Chiffre d'Affaires Exonéré / Franchise TVA (F20/C20)", "5. TVA Collectée (E4 - A)", "[COMPTE SCF 70 Franchise SC] Exonéré Art. 9 & 42 CTCA", self.ca_exonere_franchise, 0.0, 0.0),
            ("C1", "Précompte (Crédit de TVA) Reporté du Mois Précédent", "5. TVA Déductible (E4 - B)", "[COMPTE SCF 44567 SD] Report de la case (P) du mois M-1", self.tva_credit_reporte_anterior, 100.0, self.tva_credit_reporte_anterior),
            ("C2", "TVA Déductible s/ Achats de Biens et Services", "5. TVA Déductible (E4 - B)", "[COMPTE SCF 44562 SD] Justifiée par l'Annexe Fournisseurs (Art. 29 CTCA)", self.annexe_fournisseurs_total_ht, 19.0, self.tva_deductible_goods),
            ("C3", "TVA Déductible s/ Acquisitions d'Immobilisations", "5. TVA Déductible (E4 - B)", "[COMPTE SCF 44561 SD] Justifiée par l'Annexe Fournisseurs (Art. 29 CTCA)", 0.0, 19.0, self.tva_deductible_assets),
            ("E", "TVA Nette à Payer du Mois (E = max(0, A - B))", "5. Liquidation TVA (E / P)", "[COMPTE SCF 4455 SC] Formule: max(0, Total Collectée A - Total Déductible B)", self.total_tva_collectee, 0.0, self.tva_nette_a_payer),
            ("P", "Précompte de TVA à Reporter (P = max(0, B - A))", "5. Liquidation TVA (E / P)", "[COMPTE SCF 44567 SD] Formule: max(0, Total Déductible B - Total Collectée A)", self.total_tva_deductible, 0.0, self.tva_nouveau_credit),
        ]
        for code, name, cat, ref, base, rate, amt in lines_spec:
            if flt(base) != 0.0 or flt(amt) != 0.0 or code in ("C1A11", "E4L01", "C2", "E"):
                self.append("tax_lines", {
                    "code_dgi": code,
                    "tax_name": name,
                    "tax_category": cat,
                    "compte_scf_ref": ref,
                    "base_amount": flt(base),
                    "tax_rate": flt(rate),
                    "tax_amount": flt(amt),
                })

    @frappe.whitelist()
    def lock_g50_declaration(self):
        """Verrouille définitivement la déclaration G50 en lecture seule (Statut: Déposé Jibayatic)."""
        self.flags.in_lock_action = True
        self.recalculate_all_g50()
        self.status = "Déposé Jibayatic"
        self.is_g50_locked = 1
        self.save(ignore_permissions=True)
        return {"status": self.status, "is_g50_locked": self.is_g50_locked}

    @frappe.whitelist()
    def pull_from_invoices_and_payroll(self):
        """
        Extrait automatiquement les données du mois sélectionné depuis ERPNext en appliquant strictement
        l'Article 14 du CTCA et la règle de prépondérance (> 50% du TTC) sur les factures mixtes :
        1. VENTE EN L'ÉTAT (Biens >= 50% du TTC de la facture) :
           -> Fait générateur = Facturation (Sales Invoice.posting_date dans le mois M).
        2. PRESTATION DE SERVICE (Services > 50% du TTC de la facture) :
           -> Fait générateur = Encaissement (Payment Entry.posting_date dans le mois M avec payment_type='Receive').
           -> Les factures de prestations de services (ou mixtes à > 50% service) non encore encaissées au cours du mois M
              sont reportées en mémoire d'audit (TVA en attente d'encaissement) et seront intégrées automatiquement
              au mois où leur Payment Entry est validé.
        """
        if self.is_g50_locked or self.status == "Déposé Jibayatic":
            frappe.throw("🔒 Cette déclaration G50 est verrouillée en lecture seule.")

        m_num = int((self.declaration_month or "11").split("-")[0].strip())
        yr = int(self.fiscal_year or 2026)
        last_day = calendar.monthrange(yr, m_num)[1]
        start_date = f"{yr}-{m_num:02d}-01"
        end_date = f"{yr}-{m_num:02d}-{last_day:02d}"

        ca_19 = 0.0
        ca_9 = 0.0
        ca_exo = 0.0
        vent_etat_ht = 0.0
        vent_etat_tva = 0.0
        prest_enc_ht = 0.0
        prest_enc_tva = 0.0
        prest_non_enc_ht = 0.0
        prest_non_enc_tva = 0.0

        self.annexe_clients = []
        vente_etat_invoices_count = 0
        service_payments_count = 0
        mixed_invoices_count = 0

        # -------------------------------------------------------------------------
        # 1A. FACTURES ÉMISES DURANT LE MOIS M (tabSales Invoice)
        #     -> Inclure si Type Majoritaire = Vente en l'état (Biens >= 50% du TTC)
        #     -> Si Type Majoritaire = Prestation de service (> 50% du TTC), différer à l'encaissement (Payment Entry)
        # -------------------------------------------------------------------------
        month_sis = frappe.db.sql("""
            SELECT name
            FROM `tabSales Invoice`
            WHERE docstatus = 1
              AND company = %s
              AND posting_date BETWEEN %s AND %s
            ORDER BY posting_date, name
        """, (self.company, start_date, end_date), as_dict=True)

        for row_si in month_sis:
            info = classify_sales_invoice(row_si.name)
            if not info:
                continue
            si = info["si"]
            if info["is_mixed"]:
                mixed_invoices_count += 1

            if not info["is_majority_service"]:
                # Majoritaire Vente en l'état (>= 50% du TTC) => Fait générateur = Facturation (Art. 14-1 CTCA)
                vente_etat_invoices_count += 1
                ht = round(flt(si.base_net_total), 2)
                tva = round(flt(si.base_total_taxes_and_charges), 2)
                ttc = round(flt(si.base_grand_total), 2)
                nif_c = si.tax_id or si.cust_tax_id or "001616000000000"
                eff_rate = round(abs(tva / ht) * 100.0) if ht != 0 else 19

                if abs(tva) < 1.0 and ht > 0:
                    regime = "Franchise TVA F20/C20 (Exonéré Art. 9/42 CTCA)"
                    ca_exo = round(ca_exo + ht, 2)
                elif eff_rate <= 11:
                    regime = "Taxable 9% (Compte 44572 - E4L02)"
                    ca_9 = round(ca_9 + ht, 2)
                else:
                    regime = "Taxable 19% (Compte 44571 - E4L01)"
                    ca_19 = round(ca_19 + ht, 2)

                vent_etat_ht = round(vent_etat_ht + ht, 2)
                vent_etat_tva = round(vent_etat_tva + tva, 2)

                self.append("annexe_clients", {
                    "numero_facture": si.name,
                    "date_facture": si.posting_date,
                    "type_operation": info["type_operation"],
                    "facture_mixte": 1 if info["is_mixed"] else 0,
                    "part_service_ttc_pct": info["service_pct"],
                    "part_vente_etat_ttc_pct": info["bien_pct"],
                    "payment_entry_ref": None,
                    "date_encaissement": None,
                    "montant_facture_ttc_origine": ttc,
                    "client_nom": si.customer_name or si.customer,
                    "nif_client": nif_c,
                    "regime_tva_vente": regime,
                    "montant_ht": ht,
                    "montant_tva": tva,
                    "montant_ttc": ttc,
                })
            else:
                # Majoritaire Prestation de service (> 50% du TTC) :
                # Calculer la part émise ce mois mais non encore encaissée à la fin du mois M (pour mémoire d'audit CAC)
                paid_in_month = frappe.db.sql("""
                    SELECT COALESCE(SUM(per.allocated_amount), 0) as paid_ttc
                    FROM `tabPayment Entry Reference` per
                    INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
                    WHERE pe.docstatus = 1
                      AND pe.payment_type = 'Receive'
                      AND per.reference_doctype = 'Sales Invoice'
                      AND per.reference_name = %s
                      AND pe.posting_date <= %s
                """, (si.name, end_date), as_dict=True)
                paid_ttc = flt(paid_in_month[0].paid_ttc) if paid_in_month else 0.0
                rem_ttc = max(0.0, flt(si.base_grand_total) - paid_ttc)
                if rem_ttc > 0.05 and flt(si.base_grand_total) > 0:
                    ratio_unpaid = rem_ttc / flt(si.base_grand_total)
                    unpaid_ht = round(flt(si.base_net_total) * ratio_unpaid, 2)
                    unpaid_tva = round(rem_ttc - unpaid_ht, 2)
                    prest_non_enc_ht = round(prest_non_enc_ht + unpaid_ht, 2)
                    prest_non_enc_tva = round(prest_non_enc_tva + unpaid_tva, 2)

        # -------------------------------------------------------------------------
        # 1B. ENCAISSEMENTS DU MOIS M (tabPayment Entry -> Receive) SUR FACTURES DE PRESTATIONS (> 50% TTC)
        #     -> Fait générateur = Encaissement (Art. 14-2 CTCA)
        # -------------------------------------------------------------------------
        month_pes = frappe.db.sql("""
            SELECT pe.name as pe_name, pe.posting_date as pe_date, pe.mode_of_payment,
                   per.reference_name as si_name, per.allocated_amount
            FROM `tabPayment Entry` pe
            INNER JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
            WHERE pe.docstatus = 1
              AND pe.company = %s
              AND pe.payment_type = 'Receive'
              AND per.reference_doctype = 'Sales Invoice'
              AND pe.posting_date BETWEEN %s AND %s
            ORDER BY pe.posting_date, pe.name, per.idx
        """, (self.company, start_date, end_date), as_dict=True)

        for pe_row in month_pes:
            info = classify_sales_invoice(pe_row.si_name)
            if not info:
                continue
            # Seules les factures dont le type majoritaire (> 50% TTC) est 'Prestation de service'
            # sont déclarées lors de l'encaissement (les factures 'Vente en l'état' ayant déjà été déclarées à la facturation)
            if not info["is_majority_service"]:
                continue

            si = info["si"]
            service_payments_count += 1
            if info["is_mixed"] and not (str(si.posting_date) >= start_date and str(si.posting_date) <= end_date):
                mixed_invoices_count += 1

            alloc_ttc = round(flt(pe_row.allocated_amount), 2)
            orig_ttc = round(flt(si.base_grand_total), 2)
            orig_ht = round(flt(si.base_net_total), 2)
            orig_tva = round(flt(si.base_total_taxes_and_charges), 2)

            if orig_ttc != 0 and abs(alloc_ttc - orig_ttc) > 0.05:
                ratio = alloc_ttc / orig_ttc
                enc_ht = round(orig_ht * ratio, 2)
                enc_tva = round(alloc_ttc - enc_ht, 2)
            else:
                enc_ht = orig_ht
                enc_tva = orig_tva

            nif_c = si.tax_id or si.cust_tax_id or "001616000000000"
            eff_rate = round(abs(orig_tva / orig_ht) * 100.0) if orig_ht != 0 else 19

            if abs(enc_tva) < 1.0 and enc_ht > 0:
                regime = "Franchise TVA F20/C20 (Exonéré Art. 9/42 CTCA)"
                ca_exo = round(ca_exo + enc_ht, 2)
            elif eff_rate <= 11:
                regime = "Taxable 9% (Compte 44572 - E4L02)"
                ca_9 = round(ca_9 + enc_ht, 2)
            else:
                regime = "Taxable 19% (Compte 44571 - E4L01)"
                ca_19 = round(ca_19 + enc_ht, 2)

            prest_enc_ht = round(prest_enc_ht + enc_ht, 2)
            prest_enc_tva = round(prest_enc_tva + enc_tva, 2)

            self.append("annexe_clients", {
                "numero_facture": si.name,
                "date_facture": si.posting_date,
                "type_operation": info["type_operation"],
                "facture_mixte": 1 if info["is_mixed"] else 0,
                "part_service_ttc_pct": info["service_pct"],
                "part_vente_etat_ttc_pct": info["bien_pct"],
                "payment_entry_ref": pe_row.pe_name,
                "date_encaissement": pe_row.pe_date,
                "montant_facture_ttc_origine": orig_ttc,
                "client_nom": si.customer_name or si.customer,
                "nif_client": nif_c,
                "regime_tva_vente": regime,
                "montant_ht": enc_ht,
                "montant_tva": enc_tva,
                "montant_ttc": alloc_ttc,
            })

        self.ca_taxable_19 = ca_19
        self.ca_taxable_9 = ca_9
        self.ca_exonere_franchise = ca_exo
        self.ca_vente_etat_ht_mois = vent_etat_ht
        self.tva_vente_etat_mois = vent_etat_tva
        self.ca_prestation_encaisse_ht_mois = prest_enc_ht
        self.tva_prestation_encaisse_mois = prest_enc_tva
        self.ca_prestation_non_encaisse_ht_mois = prest_non_enc_ht
        self.tva_prestation_non_encaisse_mois = prest_non_enc_tva

        # -------------------------------------------------------------------------
        # 2. EXTRACTION DES FACTURES D'ACHAT (Purchase Invoice -> Annexe Fournisseurs Art. 29 & 30 CTCA)
        # -------------------------------------------------------------------------
        purchase_invoices = frappe.db.sql("""
            SELECT pi.name, pi.bill_no, pi.bill_date, pi.posting_date,
                   pi.supplier, pi.supplier_name, pi.base_net_total,
                   pi.base_total_taxes_and_charges, pi.base_grand_total,
                   s.tax_id as supp_tax_id
            FROM `tabPurchase Invoice` pi
            LEFT JOIN `tabSupplier` s ON s.name = pi.supplier
            WHERE pi.docstatus = 1
              AND pi.company = %s
              AND pi.posting_date BETWEEN %s AND %s
            ORDER BY pi.posting_date, pi.name
        """, (self.company, start_date, end_date), as_dict=True)

        self.annexe_fournisseurs = []
        for pi in purchase_invoices:
            ht = round(flt(pi.base_net_total), 2)
            tva = round(flt(pi.base_total_taxes_and_charges), 2)
            nif_f = pi.supp_tax_id or "001616000000000"
            eff_rate = "9" if (ht > 0 and round(abs(tva / ht) * 100.0) <= 11) else "19"

            pe_mode = frappe.db.sql("""
                SELECT pe.mode_of_payment
                FROM `tabPayment Entry Reference` per
                INNER JOIN `tabPayment Entry` pe ON pe.name = per.parent
                WHERE per.reference_name = %s AND pe.docstatus = 1
                LIMIT 1
            """, (pi.name,), as_dict=True)
            raw_mode = (pe_mode[0].mode_of_payment or "") if pe_mode else "Virement Bancaire"
            if "Check" in raw_mode or "Chèque" in raw_mode:
                mode_label = "Chèque Bancaire / CCP"
            elif "Cash" in raw_mode or "Espèces" in raw_mode:
                if flt(pi.base_grand_total) > 1000000.0:
                    mode_label = "Espèces (> 1 000 000 DZD TTC - Non Déductible Art. 30 CTCA)"
                else:
                    mode_label = "Espèces (<= 1 000 000 DZD TTC)"
            else:
                mode_label = "Virement Bancaire"

            self.append("annexe_fournisseurs", {
                "numero_facture": pi.bill_no or pi.name,
                "date_facture": pi.bill_date or pi.posting_date,
                "fournisseur_nom": pi.supplier_name or pi.supplier,
                "nif_fournisseur": nif_f,
                "nature_achat": "Biens et Services (Compte 44562 - C2)",
                "mode_paiement": mode_label,
                "montant_ht": ht,
                "taux_tva": eff_rate,
                "montant_tva_deduite": tva,
                "montant_ttc": round(flt(pi.base_grand_total), 2),
            })

        if not purchase_invoices:
            self.tva_deductible_goods = 0.0
            self.tva_deductible_assets = 0.0

        # -------------------------------------------------------------------------
        # 3. EXTRACTION DE LA PAIE & IRG SALAIRES (Salary Slip + GL Entries 631 & 4458/4421)
        # -------------------------------------------------------------------------
        gl_sal = frappe.db.sql("""
            SELECT
                COALESCE(SUM(CASE WHEN account LIKE '631%%' THEN debit - credit ELSE 0 END), 0) as masse_631,
                COALESCE(SUM(CASE WHEN account LIKE '4458%%' OR account LIKE '4421%%' THEN credit - debit ELSE 0 END), 0) as irg_4421
            FROM `tabGL Entry`
            WHERE is_cancelled = 0 AND company = %s AND posting_date BETWEEN %s AND %s
        """, (self.company, start_date, end_date), as_dict=True)

        ss_data = frappe.db.sql("""
            SELECT COALESCE(SUM(gross_pay), 0) as gross
            FROM `tabSalary Slip`
            WHERE docstatus = 1 AND company = %s AND posting_date BETWEEN %s AND %s
        """, (self.company, start_date, end_date), as_dict=True)

        masse_gl = flt(gl_sal[0].masse_631) if gl_sal else 0.0
        irg_gl = flt(gl_sal[0].irg_4421) if gl_sal else 0.0
        masse_ss = flt(ss_data[0].gross) if ss_data else 0.0

        self.masse_salariale_imposable = max(masse_gl, masse_ss)
        self.irg_salaries_retenu = max(0.0, irg_gl)

        # -------------------------------------------------------------------------
        # 4. REPORT DU PRÉCOMPTE DE TVA (Ligne C1) DEPUIS LE MOIS PRÉCÉDENT (M-1)
        # -------------------------------------------------------------------------
        if m_num > 1:
            prev_prefix = f"{m_num - 1:02d} -"
            prev_g50 = frappe.db.sql("""
                SELECT name, tva_nouveau_credit
                FROM `tabG50 Declaration`
                WHERE company = %s AND fiscal_year = %s AND declaration_month LIKE %s AND name != %s
                ORDER BY creation DESC LIMIT 1
            """, (self.company, self.fiscal_year, prev_prefix + "%", self.name), as_dict=True)
            if prev_g50:
                self.tva_credit_reporte_anterior = flt(prev_g50[0].tva_nouveau_credit)

        # -------------------------------------------------------------------------
        # 5. CALENDRIER DES ACOMPTES PROVISIONNELS IBS & SYNCHRONISATION DES AVANTAGES FISCAUX (Art. 356 CIDTA)
        # -------------------------------------------------------------------------
        if m_num == 3:
            self.e1m10_numero_acompte = "1er Acompte IBS (20 Février - 20 Mars : 30%)"
        elif m_num == 6:
            self.e1m10_numero_acompte = "2ème Acompte IBS (20 Mai - 20 Juin : 30%)"
        elif m_num == 11:
            self.e1m10_numero_acompte = "3ème Acompte IBS (20 Octobre - 20 Novembre : 30%)"
        else:
            self.e1m10_numero_acompte = "Aucun acompte ce mois"

        # Synchronisation automatique avec Algerian Tax Settings (si décision d'avantage fiscal en cours de validité)
        try:
            if frappe.db.exists("DocType", "Algerian Tax Settings"):
                ats = frappe.get_single("Algerian Tax Settings")
                if ats and ats.exemption_program and "Aucun" not in ats.exemption_program:
                    in_window = True
                    if ats.start_date and str(end_date) < str(ats.start_date):
                        in_window = False
                    if ats.end_date and str(start_date) > str(ats.end_date):
                        in_window = False
                    if in_window:
                        stage = ats.current_stage or ""
                        if "100%" in stage:
                            self.e1m10_dispositif_avantage = "Exonération Totale IBS 100% (AAPI / NESDA / CNAC / ANGEM / Startup)"
                            self.e1m10_taux_abattement_exo = 100.0
                        elif "70%" in stage:
                            self.e1m10_dispositif_avantage = "Abattement IBS 70% (1ère année post-exonération NESDA/CNAC)"
                            self.e1m10_taux_abattement_exo = 70.0
                        elif "50%" in stage or "Grand Sud" in (ats.exemption_program or ""):
                            self.e1m10_dispositif_avantage = "Abattement IBS 50% (Wilayas Grand Sud Art. 138 bis / 2ème année post-exo)"
                            self.e1m10_taux_abattement_exo = 50.0
                        elif "25%" in stage:
                            self.e1m10_dispositif_avantage = "Abattement IBS 25% (3ème année post-exonération NESDA/CNAC)"
                            self.e1m10_taux_abattement_exo = 25.0
                    else:
                        self.e1m10_dispositif_avantage = "Aucun (Régime de droit commun)"
                        self.e1m10_taux_abattement_exo = 0.0
        except Exception:
            pass

        self.c1a11_ca_brut_mois = self.ca_taxable_19 + self.ca_taxable_9 + self.ca_exonere_franchise
        self.recalculate_all_g50()

        return {
            "vente_etat_invoices_count": vente_etat_invoices_count,
            "service_payments_count": service_payments_count,
            "mixed_invoices_count": mixed_invoices_count,
            "sales_invoices_count": len(self.annexe_clients),
            "purchase_invoices_count": len(purchase_invoices),
            "ca_vente_etat_ht_mois": self.ca_vente_etat_ht_mois,
            "tva_vente_etat_mois": self.tva_vente_etat_mois,
            "ca_prestation_encaisse_ht_mois": self.ca_prestation_encaisse_ht_mois,
            "tva_prestation_encaisse_mois": self.tva_prestation_encaisse_mois,
            "ca_prestation_non_encaisse_ht_mois": self.ca_prestation_non_encaisse_ht_mois,
            "tva_prestation_non_encaisse_mois": self.tva_prestation_non_encaisse_mois,
            "ca_total_ht_mois": self.ca_total_ht_mois,
            "total_tva_collectee": self.total_tva_collectee,
            "total_tva_deductible": self.total_tva_deductible,
            "tva_nette_a_payer": self.tva_nette_a_payer,
            "tva_nouveau_credit": self.tva_nouveau_credit,
            "total_g50_a_payer": self.total_g50_a_payer,
            "message": (
                f"<b>Extraction Comptable & Fiscale Réussie ({self.declaration_month} {self.fiscal_year}) — Art. 14 CTCA & Règle &gt; 50% TTC :</b><br>"
                f"• <b>Ventes en l'état (Facturation, Biens &ge; 50% TTC)</b> : <b>{vente_etat_invoices_count} facture(s)</b> "
                f"(CA HT = {self.ca_vente_etat_ht_mois:,.2f} DZD | TVA = {self.tva_vente_etat_mois:,.2f} DZD)<br>"
                f"• <b>Prestations de services encaissées (Payment Entry, Services &gt; 50% TTC)</b> : <b>{service_payments_count} encaissement(s)</b> "
                f"(CA HT = {self.ca_prestation_encaisse_ht_mois:,.2f} DZD | TVA = {self.tva_prestation_encaisse_mois:,.2f} DZD)<br>"
                f"• <i>Mémoire Audit : Prestations facturées ce mois non encore encaissées (TVA différée)</i> : "
                f"CA HT = {self.ca_prestation_non_encaisse_ht_mois:,.2f} DZD | TVA différée = {self.tva_prestation_non_encaisse_mois:,.2f} DZD<br>"
                f"• <b>Total CA Imposable HT du mois (E4L01)</b> : <b>{self.ca_total_ht_mois:,.2f} DZD</b> | <b>Total TVA Collectée (A) : {self.total_tva_collectee:,.2f} DZD</b><br>"
                f"• Factures d'achat intégrées (Annexe Fournisseurs) : <b>{len(purchase_invoices)}</b> (TVA Déductible B = {self.total_tva_deductible:,.2f} DZD)<br>"
                f"• Masse salariale (631) : <b>{self.masse_salariale_imposable:,.2f} DZD</b> | IRG Salaires (4421) : <b>{self.irg_salaries_retenu:,.2f} DZD</b><br>"
                f"• TVA Nette à Payer (E) : <b>{self.tva_nette_a_payer:,.2f} DZD</b> | Précompte à Reporter (P) : <b>{self.tva_nouveau_credit:,.2f} DZD</b><br>"
                f"• <b>TOTAL GÉNÉRAL G50 À PAYER : {self.total_g50_a_payer:,.2f} DZD</b>"
            ),
        }
