# -*- coding: utf-8 -*-
app_name = "algeria_tax"
app_title = "El Tassyir El Ali | التسيير الآلي"
app_publisher = "Build And Secure Networks (BSN)"
app_description = "El Tassyir El Ali (التسيير الآلي) — Solution Intégrée de Comptabilité SCF, Fiscalité DGI (G50 / Liasse G n°4), Paie Algérienne 3-Strates (IRG / CNAS / G29), Virements Bancaires EDI & Cockpit Expert-Comptable / CAC pour ERPNext v15"
app_email = "contact@bsn-dz.com"
app_license = "gpl-3.0"
app_logo_url = "/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg"

app_include_css = ["/assets/algeria_tax/css/profi_theme.css"]
app_include_js = ["/assets/algeria_tax/js/el_tassyir_branding.js"]

website_context = {
    "favicon": "/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg",
    "splash_image": "/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg",
}

doc_events = {
    "Company": {
        "before_validate": "algeria_tax.algerian_registry.validate_company_algeria_only",
        "validate": "algeria_tax.algerian_registry.validate_company_algeria_only",
    },
    "Salary Slip": {
        "validate": "algeria_tax.payroll_engine.on_salary_slip_validate",
    },
    "Period Closing Voucher": {
        "on_submit": "algeria_tax.payroll_engine.on_period_closing_voucher_submit",
    },
}

after_install = [
    "algeria_tax.algerian_registry.seed_algerian_national_registry",
    "algeria_tax.payroll_engine.ensure_algeria_erp_indexes",
]

after_migrate = [
    "algeria_tax.algerian_registry.seed_algerian_national_registry",
    "algeria_tax.payroll_engine.ensure_algeria_erp_indexes",
]

fixtures = [
    {"dt": "Custom Field", "filters": [["name", "like", "%custom_%"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Algeria Tax"]]},
    {"dt": "Workspace", "filters": [["name", "=", "Fiscalité Algérienne"]]},
    {"dt": "Salary Component"},
    {"dt": "Salary Structure", "filters": [["name", "=", "Structure Paie Algérie SCF 2026"]]},
    {"dt": "Leave Type"},
]
