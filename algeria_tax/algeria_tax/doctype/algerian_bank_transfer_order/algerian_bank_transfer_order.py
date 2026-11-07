# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from algeria_tax.algerian_registry import validate_algerian_rib, ALGERIAN_BANKS
from algeria_tax.bank_transfer_engine import (
    amount_to_words_dzd_fr,
    amount_to_words_dzd_ar,
    generate_satim_edi_transfer_file,
    render_official_bank_transfer_html,
)


class AlgerianBankTransferOrder(Document):
    def validate(self):
        # 1. Valider le RIB du donneur d'ordre (20 chiffres)
        if self.emitter_rib:
            res_em = validate_algerian_rib(self.emitter_rib)
            self.emitter_rib_valid = 1 if res_em["is_valid"] else 0
            if res_em.get("bank_code"):
                self.emitter_bank_code = res_em["bank_code"]
                self.emitter_bank_name = res_em["bank_name"]
                self.emitter_swift_bic = res_em["swift_bic"]

        # 2. Calculer le total et valider chaque ligne bénéficiaire
        total = 0.0
        lines_list = []
        for row in (self.get("lines") or []):
            amt = round(flt(row.amount), 2)
            total += amt
            if row.beneficiary_rib:
                r_check = validate_algerian_rib(row.beneficiary_rib)
                row.rib_valid = 1 if r_check["is_valid"] else 0
                if not row.beneficiary_bank and r_check.get("bank_name"):
                    row.beneficiary_bank = r_check["bank_name"]
            lines_list.append({
                "beneficiary_name": row.beneficiary_name,
                "beneficiary_bank": row.beneficiary_bank,
                "beneficiary_rib": row.beneficiary_rib,
                "payment_reference": row.payment_reference,
                "amount": amt,
            })

        self.total_beneficiaries = len(lines_list)
        self.total_amount = round(total, 2)
        self.amount_in_words_fr = amount_to_words_dzd_fr(self.total_amount)
        self.amount_in_words_ar = amount_to_words_dzd_ar(self.total_amount)

        # 3. Générer le fichier magnétique EDI Télécompensation SATIM
        self.edi_satim_content = generate_satim_edi_transfer_file(
            order_name=self.name or self.order_reference or "OV-001",
            execution_date=str(self.posting_date or ""),
            company_name=self.company or "ENTREPRISE",
            emitter_rib_20=self.emitter_rib or "",
            lines=lines_list,
            transfer_motif=self.transfer_type or "VIREMENT",
        )

    @frappe.whitelist()
    def get_official_print_html(self):
        lines_list = [
            {
                "beneficiary_name": r.beneficiary_name,
                "beneficiary_bank": r.beneficiary_bank,
                "beneficiary_rib": r.beneficiary_rib,
                "payment_reference": r.payment_reference,
                "amount": flt(r.amount),
            }
            for r in (self.get("lines") or [])
        ]
        return render_official_bank_transfer_html({
            "name": self.name or self.order_reference,
            "transfer_type": self.transfer_type,
            "posting_date": str(self.posting_date),
            "company": self.company,
            "company_nif": self.company_nif,
            "emitter_bank_code": self.emitter_bank_code or "001",
            "emitter_branch": self.emitter_branch or "Agence Principale",
            "emitter_rib": self.emitter_rib,
            "scf_debit_account": self.scf_debit_account,
            "scf_credit_account": self.scf_credit_account,
            "total_amount": self.total_amount,
            "amount_in_words_fr": self.amount_in_words_fr,
            "amount_in_words_ar": self.amount_in_words_ar,
            "lines": lines_list,
        })
