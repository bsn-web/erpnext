frappe.ui.form.on('Bilan Fiscal', {
    refresh: function(frm) {
        // Contrôle du statut de clôture & Verrouillage strict en lecture seule
        if (frm.doc.is_fiscal_closed || frm.doc.status === "Clôturé & Verrouillé (Lecture Seule)" || frm.doc.docstatus === 1) {
            frm.disable_save();
            frm.set_read_only();
            frm.dashboard.set_headline_alert(
                __("Liasse Fiscale Clôturée : Ce bilan officiel a été déposé et verrouillé en lecture seule. Aucune modification n'est permise."),
                "orange"
            );
        } else {
            // Bouton de clôture définitive
            frm.add_custom_button(__('Clôturer & Verrouiller l\'Exercice'), function() {
                frappe.confirm(
                    __("Êtes-vous sûr de vouloir clôturer et verrouiller définitivement ce Bilan Fiscal ? Après cette action, le document deviendra strictement en lecture seule."),
                    function() {
                        frm.call({
                            method: "lock_bilan_fiscal",
                            doc: frm.doc,
                            callback: function() {
                                frm.reload_doc();
                            }
                        });
                    }
                );
            }).addClass('btn-danger');
        }

        // Bouton d'impression format officiel DGI / DCI
        frm.add_custom_button(__('Imprimer Liasse DCI (12 Pages)'), function() {
            var print_url = frappe.urllib.get_full_url(
                "/printview?doctype=" + encodeURIComponent(frm.doc.doctype) +
                "&name=" + encodeURIComponent(frm.doc.name) +
                "&print_format=" + encodeURIComponent("Bilan Fiscal DCI") +
                "&no_letterhead=1"
            );
            window.open(print_url, "_blank");
        }).addClass('btn-primary');
    }
});
