# -*- coding: utf-8 -*-
"""
El Tassyir El Ali (التسيير الآلي) — Moteur d'Ordres de Virement Bancaire & Fichiers EDI Télécompensation Algérie
Supporte :
1. Les 22 Banques Algériennes (BNA, BEA, BADR, CPA, BDL, Al Baraka, CNEP, SGA, AGB, BNP Paribas, Al Salam, Trust, HBTF, Fransabank, ABC, Natixis, Citibank, Arab Bank...) + CCP Algérie Poste + Trésor Public.
2. Les 4 flux de virement :
   - Virement Collectif de Salaires (Paie Mensuelle -> Débit 421 / Crédit 512)
   - Virement Fiscal DGI (Paiement G50 / Solde IBS -> Débit 442..447 / Crédit 512)
   - Virement Social & Parafiscal (CNAS 35% / CASNOS 15% / CACOBATPH -> Débit 431..432 / Crédit 512)
   - Virement Fournisseur & Assurance (SAA, CAAR, CAAT, CIAR, Alliance, CASH, etc. -> Débit 401 / Crédit 512)
3. Génération du fichier magnétique EDI Télécompensation SATIM (Norme Banque d'Algérie RIB 20 chiffres) et CSV CCP.
4. Conversion automatique des montants en toutes lettres (Français & Arabe) en Dinars Algériens et Centimes.
"""

import re
from datetime import date
from algeria_tax.algerian_registry import (
    ALGERIAN_BANKS,
    validate_algerian_rib,
    compute_algerian_rib_key,
)

try:
    import frappe
    from frappe.utils import flt
except ImportError:
    frappe = None
    def flt(val):
        try:
            return float(val or 0.0)
        except Exception:
            return 0.0


# ==============================================================================
# 1. CONVERSION DES MONTANTS EN TOUTES LETTRES (DZD — FRANÇAIS & ARABE)
# ==============================================================================
_UNITS_FR = [
    "", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
    "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize",
    "dix-sept", "dix-huit", "dix-neuf"
]
_TENS_FR = [
    "", "dix", "vingt", "trente", "quarante", "cinquante",
    "soixante", "soixante", "quatre-vingt", "quatre-vingt"
]


def _int_to_words_fr_under_1000(n: int) -> str:
    if n == 0:
        return ""
    parts = []
    hundreds = n // 100
    rem = n % 100
    if hundreds > 0:
        if hundreds == 1:
            parts.append("cent")
        else:
            parts.append(f"{_UNITS_FR[hundreds]} cent" + ("s" if rem == 0 else ""))
    if rem > 0:
        if rem < 20:
            parts.append(_UNITS_FR[rem])
        else:
            t = rem // 10
            u = rem % 10
            if t in (7, 9):
                base = _TENS_FR[t]
                sub = 10 + u
                sep = "-et-" if (t == 7 and u == 1) else "-"
                parts.append(f"{base}{sep}{_UNITS_FR[sub]}")
            else:
                base = _TENS_FR[t]
                if u == 0:
                    parts.append(base + ("s" if t == 8 else ""))
                elif u == 1 and t != 8:
                    parts.append(f"{base}-et-un")
                else:
                    parts.append(f"{base}-{_UNITS_FR[u]}")
    return " ".join(parts)


def _int_to_words_fr(n: int) -> str:
    if n == 0:
        return "zéro"
    chunks = []
    billions = n // 1_000_000_000
    millions = (n % 1_000_000_000) // 1_000_000
    thousands = (n % 1_000_000) // 1_000
    rest = n % 1_000

    if billions > 0:
        w = _int_to_words_fr_under_1000(billions)
        chunks.append(f"{w} milliard" + ("s" if billions > 1 else ""))
    if millions > 0:
        w = _int_to_words_fr_under_1000(millions)
        chunks.append(f"{w} million" + ("s" if millions > 1 else ""))
    if thousands > 0:
        if thousands == 1:
            chunks.append("mille")
        else:
            chunks.append(f"{_int_to_words_fr_under_1000(thousands)} mille")
    if rest > 0:
        chunks.append(_int_to_words_fr_under_1000(rest))
    return " ".join(chunks).strip()


def amount_to_words_dzd_fr(amount: float) -> str:
    """
    Convertit un montant en Dinars Algériens en toutes lettres (Français réglementaire bancaire).
    Exemple : 165656.83 -> 'Cent soixante-cinq mille six cent cinquante-six Dinars Algériens et 83 Centimes'
    """
    val = round(abs(flt(amount)), 2)
    dinars = int(val)
    centimes = int(round((val - dinars) * 100))
    words_d = _int_to_words_fr(dinars).capitalize()
    unit_d = "Dinar Algérien" if dinars <= 1 else "Dinars Algériens"
    if centimes > 0:
        return f"{words_d} {unit_d} et {centimes:02d} Centimes"
    return f"{words_d} {unit_d} et 00 Centime"


def amount_to_words_dzd_ar(amount: float) -> str:
    """
    Formate la mention officielle en arabe pour les ordres de virement bancaires algériens.
    """
    val = round(abs(flt(amount)), 2)
    dinars = int(val)
    centimes = int(round((val - dinars) * 100))
    formatted_dinars = f"{dinars:,}".replace(",", " ")
    if centimes > 0:
        return f"{formatted_dinars} دينار جزائري و {centimes:02d} سنتيم"
    return f"{formatted_dinars} دينار جزائري و 00 سنتيم"


# ==============================================================================
# 2. GÉNÉRATEUR DE FICHIER MAGNÉTIQUE EDI TÉLÉCOMPENSATION SATIM (BANQUE D'ALGÉRIE)
# ==============================================================================
def generate_satim_edi_transfer_file(
    order_name: str,
    execution_date: str,
    company_name: str,
    emitter_rib_20: str,
    lines: list,
    transfer_motif: str = "VIREMENT SALAIRES",
) -> str:
    """
    Génère le fichier texte EDI interbancaire au format Télécompensation Algérie (SATIM / Banque d'Algérie) :
    - Enregistrement En-tête '01' (Donneur d'ordre : Société + RIB 20 chiffres + Date + Nombre de lignes + Total en centimes)
    - Enregistrements Détail '02' (Bénéficiaire : Séquence + Nom + RIB 20 chiffres + Montant en centimes + Motif)
    - Enregistrement Total '09' (Contrôle de pied : Nombre total d'opérations + Somme en centimes)
    """
    clean_emitter_rib = re.sub(r"\D", "", str(emitter_rib_20 or "")).zfill(20)[:20]
    dt_str = re.sub(r"\D", "", str(execution_date or str(date.today())))[:8]
    if len(dt_str) != 8:
        dt_str = date.today().strftime("%Y%m%d")

    comp_clean = re.sub(r"[^A-Za-z0-9 ]", " ", str(company_name or "ENTREPRISE")).upper()[:35].ljust(35)
    ref_clean = re.sub(r"[^A-Za-z0-9\-]", "", str(order_name or "OV-001")).upper()[:16].ljust(16)

    total_centimes = 0
    detail_records = []

    for idx, row in enumerate(lines, start=1):
        amt = round(flt(row.get("amount", 0.0)), 2)
        if amt <= 0:
            continue
        amt_c = int(round(amt * 100))
        total_centimes += amt_c

        ben_name = re.sub(r"[^A-Za-z0-9 ]", " ", str(row.get("beneficiary_name") or "")).upper()[:35].ljust(35)
        ben_rib = re.sub(r"\D", "", str(row.get("beneficiary_rib") or "")).zfill(20)[:20]
        motif = re.sub(r"[^A-Za-z0-9 ]", " ", str(row.get("payment_reference") or transfer_motif)).upper()[:30].ljust(30)

        rec_02 = f"02{idx:06d}{ben_rib}{ben_name}{amt_c:015d}{motif}"
        detail_records.append(rec_02)

    count_ops = len(detail_records)
    rec_01 = f"01{dt_str}{clean_emitter_rib}{comp_clean}{ref_clean}{count_ops:06d}{total_centimes:015d}"
    rec_09 = f"09{count_ops:06d}{total_centimes:015d}{clean_emitter_rib}"

    return "\r\n".join([rec_01] + detail_records + [rec_09]) + "\r\n"


# ==============================================================================
# 3. GÉNÉRATEUR HTML D'ORDRE DE VIREMENT BANCAIRE OFFICIEL (MULTI-BANQUES ALGÉRIE)
# ==============================================================================
def render_official_bank_transfer_html(order_dict: dict) -> str:
    """
    Génère le document HTML officiel prêt à imprimer et signer (Cachet & Signature Gérant)
    pour toutes les banques algériennes (BNA, BEA, CPA, BADR, BDL, CNEP, SGA, AGB, BNP Paribas, Al Baraka, Al Salam, CCP).
    """
    bank_code = order_dict.get("emitter_bank_code") or "001"
    bank_map = {b["bank_code"]: b for b in ALGERIAN_BANKS}
    bank_info = bank_map.get(bank_code, ALGERIAN_BANKS[0])

    total_amount = round(flt(order_dict.get("total_amount", 0.0)), 2)
    words_fr = order_dict.get("amount_in_words_fr") or amount_to_words_dzd_fr(total_amount)
    words_ar = order_dict.get("amount_in_words_ar") or amount_to_words_dzd_ar(total_amount)
    lines = order_dict.get("lines") or []

    rows_html = []
    for idx, line in enumerate(lines, start=1):
        rib_fmt = validate_algerian_rib(line.get("beneficiary_rib", "")).get("formatted_rib") or line.get("beneficiary_rib", "")
        amt_fmt = f"{flt(line.get('amount', 0.0)):,.2f}".replace(",", " ")
        rows_html.append(f"""
        <tr>
            <td style="text-align:center; padding:6px; border:1px solid #cbd5e1;">{idx}</td>
            <td style="padding:6px; border:1px solid #cbd5e1; font-weight:600;">{line.get('beneficiary_name', '')}</td>
            <td style="padding:6px; border:1px solid #cbd5e1;">{line.get('beneficiary_bank', '')}</td>
            <td style="padding:6px; border:1px solid #cbd5e1; font-family:monospace; font-size:12px;">{rib_fmt}</td>
            <td style="padding:6px; border:1px solid #cbd5e1;">{line.get('payment_reference', '')}</td>
            <td style="text-align:right; padding:6px; border:1px solid #cbd5e1; font-weight:700;">{amt_fmt} DZD</td>
        </tr>
        """)

    total_fmt = f"{total_amount:,.2f}".replace(",", " ")
    emitter_rib_fmt = validate_algerian_rib(order_dict.get("emitter_rib", "")).get("formatted_rib") or order_dict.get("emitter_rib", "")

    return f"""
    <div style="font-family:'Inter', 'Segoe UI', Arial, sans-serif; color:#0f172a; padding:24px; max-width:960px; margin:auto; border:2px solid #1e3a8a; border-radius:8px; background:#ffffff;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #1e3a8a; padding-bottom:14px; margin-bottom:18px;">
            <div>
                <div style="font-size:12px; color:#475569; text-transform:uppercase; letter-spacing:1px;">El Tassyir El Ali — التسيير الآلي</div>
                <h2 style="margin:4px 0; color:#1e3a8a; font-size:20px;">ORDRE DE VIREMENT BANCAIRE / أمر بتحويل بنكي</h2>
                <div style="font-size:13px; font-weight:600; color:#334155;">
                    Type : {order_dict.get('transfer_type', 'Virement Bancaire')} | N° : {order_dict.get('name', 'OV-2026-001')}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:15px; font-weight:700; color:#1e3a8a;">{bank_info['bank_name']}</div>
                <div style="font-size:14px; color:#0f172a; direction:rtl;">{bank_info['bank_name_ar']}</div>
                <div style="font-size:12px; color:#475569;">Code Banque BA : <b>{bank_info['bank_code']}</b> | BIC/SWIFT : <b>{bank_info['swift_bic']}</b></div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:18px; background:#f8fafc; padding:14px; border:1px solid #e2e8f0; border-radius:6px;">
            <div>
                <div style="font-size:11px; text-transform:uppercase; color:#64748b; font-weight:700;">Donneur d'Ordre (Société Émettrice / الآمر بالدفع)</div>
                <div style="font-size:14px; font-weight:700; margin-top:4px;">{order_dict.get('company', '')}</div>
                <div style="font-size:12px; color:#334155;">NIF : {order_dict.get('company_nif', '')} | Agence : {order_dict.get('emitter_branch', 'Agence Centrale')}</div>
                <div style="font-size:13px; font-family:monospace; margin-top:4px; font-weight:700; color:#1e3a8a;">RIB Donneur d'Ordre : {emitter_rib_fmt}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px; text-transform:uppercase; color:#64748b; font-weight:700;">Références d'Exécution / مراجع التنفيذ</div>
                <div style="font-size:13px; margin-top:4px;">Date d'émission : <b>{order_dict.get('posting_date', str(date.today()))}</b></div>
                <div style="font-size:13px;">Compte SCF débité : <b>{order_dict.get('scf_debit_account', '421 / 401 / 431 / 442')}</b></div>
                <div style="font-size:13px;">Compte SCF crédité : <b>{order_dict.get('scf_credit_account', '512 - Banques comptes courants')}</b></div>
            </div>
        </div>

        <p style="font-size:13px; line-height:1.5; margin-bottom:12px;">
            Messieurs,<br/>
            Par le débit de notre compte bancaire N° <b>{emitter_rib_fmt}</b> ouvert auprès de votre agence, nous vous prions de bien vouloir exécuter le(s) virement(s) ci-après :
        </p>

        <table style="width:100%; border-collapse:collapse; font-size:12px; margin-bottom:16px;">
            <thead>
                <tr style="background:#1e3a8a; color:#ffffff;">
                    <th style="padding:8px; border:1px solid #1e3a8a; width:40px;">N°</th>
                    <th style="padding:8px; border:1px solid #1e3a8a; text-align:left;">Nom / Raison Sociale du Bénéficiaire (المستفيد)</th>
                    <th style="padding:8px; border:1px solid #1e3a8a; text-align:left;">Banque / Agence</th>
                    <th style="padding:8px; border:1px solid #1e3a8a; text-align:left;">RIB Bénéficiaire (20 chiffres)</th>
                    <th style="padding:8px; border:1px solid #1e3a8a; text-align:left;">Motif / Référence</th>
                    <th style="padding:8px; border:1px solid #1e3a8a; text-align:right;">Montant (DZD)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows_html)}
            </tbody>
            <tfoot>
                <tr style="background:#f1f5f9; font-weight:700; font-size:13px;">
                    <td colspan="5" style="padding:8px; border:1px solid #cbd5e1; text-align:right;">TOTAL GÉNÉRAL À VIRER ({len(lines)} bénéficiaire(s)) / المجموع الإجمالي :</td>
                    <td style="padding:8px; border:1px solid #cbd5e1; text-align:right; color:#1e3a8a; font-size:14px;">{total_fmt} DZD</td>
                </tr>
            </tfoot>
        </table>

        <div style="background:#eff6ff; border-left:4px solid #1e3a8a; padding:12px; margin-bottom:24px; font-size:13px;">
            <div><b>Arrêté le présent ordre de virement à la somme de :</b> {words_fr}.</div>
            <div style="direction:rtl; margin-top:4px;"><b>أوقف هذا الأمر بالتحويل عند مبلغ :</b> {words_ar}.</div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-top:28px; font-size:12px;">
            <div style="border:1px dashed #94a3b8; padding:14px; min-height:90px; border-radius:6px;">
                <b>Cadre réservé à la Banque ({bank_info['abbr']}) :</b><br/>
                Date de réception : ____/____/2026<br/>
                Visa & Cachet de l'Agence :
            </div>
            <div style="border:1px dashed #94a3b8; padding:14px; min-height:90px; border-radius:6px; text-align:right;">
                <b>Signature(s) Autorisée(s) & Cachet Humide du Donneur d'Ordre :</b><br/>
                ({order_dict.get('company', '')})
            </div>
        </div>
    </div>
    """
