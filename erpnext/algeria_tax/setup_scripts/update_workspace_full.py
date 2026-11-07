import frappe
import json
import uuid

frappe.init(site='frappe.com')
frappe.connect()

def gen_id():
    return uuid.uuid4().hex[:10]

ws_name = "Fiscalité Algérienne"
if frappe.db.exists("Workspace", ws_name):
    frappe.delete_doc("Workspace", ws_name, force=1)
    frappe.db.commit()

ws = frappe.new_doc("Workspace")
ws.name = ws_name
ws.label = ws_name
ws.title = ws_name
ws.category = "Modules"
ws.is_standard = 0
ws.public = 1
ws.module = "Algeria Tax"
ws.icon = "calculator"

# --- 1. SHORTCUTS ---
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Déclarations G50",
    "link_to": "G50 Declaration",
    "doc_view": "List",
    "color": "Blue"
})
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Tableau 9 IBS",
    "link_to": "Fiscal Table 9 Engine",
    "doc_view": "List",
    "color": "Green"
})
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Acomptes IBS",
    "link_to": "IBS Installment Schedule",
    "doc_view": "List",
    "color": "Orange"
})
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Attestations C20",
    "link_to": "Attestation Franchise TVA",
    "doc_view": "List",
    "color": "Purple"
})
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Paramètres Fiscaux",
    "link_to": "Algerian Tax Settings",
    "color": "Grey"
})
ws.append("shortcuts", {
    "type": "DocType",
    "label": "Plan Comptable SCF",
    "link_to": "Account",
    "color": "Grey"
})

# --- 2. LINKS (CARDS) ---
# Card 1
ws.append("links", {
    "type": "Card Break",
    "label": "Déclarations Fiscales & G50",
    "icon": "calculator"
})
ws.append("links", {
    "type": "Link",
    "label": "Déclaration Mensuelle G50",
    "link_type": "DocType",
    "link_to": "G50 Declaration"
})
ws.append("links", {
    "type": "Link",
    "label": "Acomptes Provisionnels IBS (30%)",
    "link_type": "DocType",
    "link_to": "IBS Installment Schedule"
})
ws.append("links", {
    "type": "Link",
    "label": "Liasse Fiscale - Tableau 9 (IBS)",
    "link_type": "DocType",
    "link_to": "Fiscal Table 9 Engine"
})

# Card 2
ws.append("links", {
    "type": "Card Break",
    "label": "Régimes Particuliers & Exonérations",
    "icon": "award"
})
ws.append("links", {
    "type": "Link",
    "label": "Attestations Franchise TVA (C20)",
    "link_type": "DocType",
    "link_to": "Attestation Franchise TVA"
})
ws.append("links", {
    "type": "Link",
    "label": "Paramètres Fiscaux Algérie",
    "link_type": "DocType",
    "link_to": "Algerian Tax Settings"
})

# Card 3
ws.append("links", {
    "type": "Card Break",
    "label": "Comptabilité SCF & Contrôles",
    "icon": "shield"
})
ws.append("links", {
    "type": "Link",
    "label": "Plan Comptable Général SCF",
    "link_type": "DocType",
    "link_to": "Account"
})
ws.append("links", {
    "type": "Link",
    "label": "Écritures de Journal (OD)",
    "link_type": "DocType",
    "link_to": "Journal Entry"
})
ws.append("links", {
    "type": "Link",
    "label": "Paiements & Contrôle Caisse",
    "link_type": "DocType",
    "link_to": "Payment Entry"
})

# --- 3. CONTENT BLOCKS ---
blocks = [
    {
        "id": gen_id(),
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>Accès Rapide</b></span>",
            "col": 12
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Déclarations G50",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Tableau 9 IBS",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Acomptes IBS",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Attestations C20",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Paramètres Fiscaux",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "shortcut",
        "data": {
            "shortcut_name": "Plan Comptable SCF",
            "col": 3
        }
    },
    {
        "id": gen_id(),
        "type": "spacer",
        "data": {
            "col": 12
        }
    },
    {
        "id": gen_id(),
        "type": "header",
        "data": {
            "text": "<span class=\"h4\"><b>Modules & Déclarations Fiscales</b></span>",
            "col": 12
        }
    },
    {
        "id": gen_id(),
        "type": "card",
        "data": {
            "card_name": "Déclarations Fiscales & G50",
            "col": 4
        }
    },
    {
        "id": gen_id(),
        "type": "card",
        "data": {
            "card_name": "Régimes Particuliers & Exonérations",
            "col": 4
        }
    },
    {
        "id": gen_id(),
        "type": "card",
        "data": {
            "card_name": "Comptabilité SCF & Contrôles",
            "col": 4
        }
    }
]

ws.content = json.dumps(blocks)
ws.insert(ignore_permissions=True)
frappe.db.commit()
print("Saved Workspace with full content blocks!")
