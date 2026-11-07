// El Tassyir El Ali (التسيير الآلي) — Branding & Restriction Algérie Uniquement
frappe.provide("el_tassyir_el_ali");

$(document).on("app_ready", function () {
    // 1. Renommer le titre de l'application dans l'interface Desk
    if (document.title.indexOf("ERPNext") !== -1 || document.title.indexOf("Frappe") !== -1) {
        document.title = "El Tassyir El Ali | التسيير الآلي — Comptabilité SCF & Gestion Algérie";
    }
    const brandImg = document.querySelector(".navbar-brand img");
    if (brandImg) {
        brandImg.src = "/assets/algeria_tax/images/el_tassyir_el_ali_logo.svg";
        brandImg.style.maxHeight = "38px";
        brandImg.style.width = "auto";
    }
});

// 2. Forcer et verrouiller Country = 'Algeria' et Default Currency = 'DZD' sur toute création d'entreprise
frappe.ui.form.on("Company", {
    onload: function (frm) {
        if (frm.is_new() || frm.doc.country !== "Algeria") {
            frm.set_value("country", "Algeria");
        }
        if (frm.is_new() || frm.doc.default_currency !== "DZD") {
            frm.set_value("default_currency", "DZD");
        }
        frm.set_df_property("country", "read_only", 1);
        frm.set_df_property("default_currency", "read_only", 1);
        frm.set_df_property("country", "description", "Verrouillé sur l'Algérie (El Tassyir El Ali — التسيير الآلي)");
    },
    validate: function (frm) {
        if (frm.doc.country && frm.doc.country !== "Algeria") {
            frappe.throw(__("El Tassyir El Ali (التسيير الآلي) autorise uniquement la création d'entreprises domiciliées en Algérie (Country = Algeria)."));
        }
        if (frm.doc.default_currency && frm.doc.default_currency !== "DZD") {
            frappe.throw(__("La devise comptable SCF obligatoire en Algérie est le Dinar Algérien (DZD)."));
        }
    }
});
