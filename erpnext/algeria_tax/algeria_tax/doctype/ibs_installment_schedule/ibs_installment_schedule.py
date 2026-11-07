import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class IBSInstallmentSchedule(Document):
    def validate(self):
        ref = flt(self.reference_ibs_n1)
        if not self.is_first_year_exempt:
            self.acompte_1_amount = round(ref * 0.30, 2)
            self.acompte_2_amount = round(ref * 0.30, 2)
            self.acompte_3_amount = round(ref * 0.30, 2)
        else:
            self.acompte_1_amount = 0.0
            self.acompte_2_amount = 0.0
            self.acompte_3_amount = 0.0
            
        paid_total = 0.0
        if self.acompte_1_paid: paid_total += self.acompte_1_amount
        if self.acompte_2_paid: paid_total += self.acompte_2_amount
        if self.acompte_3_paid: paid_total += self.acompte_3_amount
        self.total_acomptes_paid = paid_total
        
        if flt(self.actual_ibs_due) > 0:
            diff = flt(self.actual_ibs_due) - self.total_acomptes_paid
            if diff > 0:
                self.solde_a_payer = diff
                self.credit_ibs_reportable = 0.0
            else:
                self.solde_a_payer = 0.0
                self.credit_ibs_reportable = abs(diff)
