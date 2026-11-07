# Algerian SCF (Système Comptable Financier) Complete Standardized Tree
# Conforme à la loi 07-11 et à l'arrêté du 26 juillet 2008

SCF_TREE = {
    # -------------------------------------------------------------------------
    # 1. ACTIF (Root: Asset, Report: Balance Sheet)
    # Parent: 1000 - Application of Funds (Assets) - BSN
    # -------------------------------------------------------------------------
    "ACTIF": {
        "number": "SCF-ACTIF",
        "name": "SCF - Plan Comptable Financier (Actif)",
        "root_type": "Asset",
        "report_type": "Balance Sheet",
        "is_group": 1,
        "children": {
            # --- CLASSE 2 : IMMOBILISATIONS ---
            "SCF-2": {
                "number": "SCF-2",
                "name": "Classe 2 : Comptes d'immobilisations",
                "is_group": 1,
                "children": {
                    "SCF-20": {
                        "number": "SCF-20",
                        "name": "Immobilisations incorporelles",
                        "is_group": 1,
                        "account_type": "Fixed Asset",
                        "children": {
                            "SCF-203": {"number": "SCF-203", "name": "Frais de développement immobilisables", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-204": {"number": "SCF-204", "name": "Logiciels informatiques et assimilés", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-205": {"number": "SCF-205", "name": "Concessions, brevets, licences, marques", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-207": {"number": "SCF-207", "name": "Écart d'acquisition (Goodwill)", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-208": {"number": "SCF-208", "name": "Autres immobilisations incorporelles", "is_group": 0, "account_type": "Fixed Asset"},
                        }
                    },
                    "SCF-21": {
                        "number": "SCF-21",
                        "name": "Immobilisations corporelles",
                        "is_group": 1,
                        "account_type": "Fixed Asset",
                        "children": {
                            "SCF-211": {
                                "number": "SCF-211",
                                "name": "Terrains",
                                "is_group": 1,
                                "account_type": "Fixed Asset",
                                "children": {
                                    "SCF-2111": {"number": "SCF-2111", "name": "Terrains nus", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2115": {"number": "SCF-2115", "name": "Terrains bâtis", "is_group": 0, "account_type": "Fixed Asset"},
                                }
                            },
                            "SCF-212": {"number": "SCF-212", "name": "Agencements et aménagements de terrains", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-213": {
                                "number": "SCF-213",
                                "name": "Constructions",
                                "is_group": 1,
                                "account_type": "Fixed Asset",
                                "children": {
                                    "SCF-2131": {"number": "SCF-2131", "name": "Bâtiments d'exploitation", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2135": {"number": "SCF-2135", "name": "Installations générales et agencements des constructions", "is_group": 0, "account_type": "Fixed Asset"},
                                }
                            },
                            "SCF-215": {
                                "number": "SCF-215",
                                "name": "Installations techniques, matériel et outillage industriels",
                                "is_group": 1,
                                "account_type": "Fixed Asset",
                                "children": {
                                    "SCF-2151": {"number": "SCF-2151", "name": "Installations techniques", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2154": {"number": "SCF-2154", "name": "Matériel industriel et machines", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2155": {"number": "SCF-2155", "name": "Outillage industriel", "is_group": 0, "account_type": "Fixed Asset"},
                                }
                            },
                            "SCF-218": {
                                "number": "SCF-218",
                                "name": "Autres immobilisations corporelles",
                                "is_group": 1,
                                "account_type": "Fixed Asset",
                                "children": {
                                    "SCF-2181": {"number": "SCF-2181", "name": "Installations générales et agencements divers", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2182": {"number": "SCF-2182", "name": "Matériel de transport", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2183": {"number": "SCF-2183", "name": "Matériel de bureau et matériel informatique", "is_group": 0, "account_type": "Fixed Asset"},
                                    "SCF-2184": {"number": "SCF-2184", "name": "Mobilier de bureau", "is_group": 0, "account_type": "Fixed Asset"},
                                }
                            }
                        }
                    },
                    "SCF-22": {
                        "number": "SCF-22",
                        "name": "Terrains et aménagements mis en concession",
                        "is_group": 1,
                        "account_type": "Fixed Asset",
                        "children": {
                            "SCF-221": {"number": "SCF-221", "name": "Terrains en concession", "is_group": 0, "account_type": "Fixed Asset"},
                            "SCF-222": {"number": "SCF-222", "name": "Aménagements de terrains en concession", "is_group": 0, "account_type": "Fixed Asset"},
                        }
                    },
                    "SCF-23": {
                        "number": "SCF-23",
                        "name": "Immobilisations en cours",
                        "is_group": 1,
                        "account_type": "Capital Work in Progress",
                        "children": {
                            "SCF-232": {"number": "SCF-232", "name": "Immobilisations corporelles en cours", "is_group": 0, "account_type": "Capital Work in Progress"},
                            "SCF-237": {"number": "SCF-237", "name": "Immobilisations incorporelles en cours", "is_group": 0, "account_type": "Capital Work in Progress"},
                            "SCF-238": {"number": "SCF-238", "name": "Avances et acomptes versés sur commandes d'immobilisations", "is_group": 0, "account_type": "Capital Work in Progress"},
                        }
                    },
                    "SCF-26": {
                        "number": "SCF-26",
                        "name": "Participations et créances rattachées à des participations",
                        "is_group": 1,
                        "children": {
                            "SCF-261": {"number": "SCF-261", "name": "Titres de filiales", "is_group": 0},
                            "SCF-262": {"number": "SCF-262", "name": "Autres titres de participation", "is_group": 0},
                            "SCF-266": {"number": "SCF-266", "name": "Créances rattachées à des participations (groupe)", "is_group": 0},
                        }
                    },
                    "SCF-27": {
                        "number": "SCF-27",
                        "name": "Autres immobilisations financières",
                        "is_group": 1,
                        "children": {
                            "SCF-271": {"number": "SCF-271", "name": "Titres immobilisés autres que les titres de participation", "is_group": 0},
                            "SCF-274": {"number": "SCF-274", "name": "Prêts", "is_group": 0},
                            "SCF-275": {"number": "SCF-275", "name": "Dépôts et cautionnements versés", "is_group": 0},
                        }
                    },
                    "SCF-28": {
                        "number": "SCF-28",
                        "name": "Amortissements des immobilisations",
                        "is_group": 1,
                        "account_type": "Accumulated Depreciation",
                        "children": {
                            "SCF-280": {
                                "number": "SCF-280",
                                "name": "Amortissement des immobilisations incorporelles",
                                "is_group": 1,
                                "account_type": "Accumulated Depreciation",
                                "children": {
                                    "SCF-2804": {"number": "SCF-2804", "name": "Amortissement des logiciels informatiques", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                    "SCF-2805": {"number": "SCF-2805", "name": "Amortissement des concessions, brevets, licences", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                    "SCF-2808": {"number": "SCF-2808", "name": "Amortissement des autres immobilisations incorporelles", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                }
                            },
                            "SCF-281": {
                                "number": "SCF-281",
                                "name": "Amortissement des immobilisations corporelles",
                                "is_group": 1,
                                "account_type": "Accumulated Depreciation",
                                "children": {
                                    "SCF-2812": {"number": "SCF-2812", "name": "Amortissement des aménagements de terrains", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                    "SCF-2813": {"number": "SCF-2813", "name": "Amortissement des constructions", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                    "SCF-2815": {"number": "SCF-2815", "name": "Amortissement des installations techniques, matériel et outillage", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                    "SCF-2818": {
                                        "number": "SCF-2818",
                                        "name": "Amortissement des autres immobilisations corporelles",
                                        "is_group": 1,
                                        "account_type": "Accumulated Depreciation",
                                        "children": {
                                            "SCF-28182": {"number": "SCF-28182", "name": "Amortissement du matériel de transport", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                            "SCF-28183": {"number": "SCF-28183", "name": "Amortissement du matériel de bureau et informatique", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                            "SCF-28184": {"number": "SCF-28184", "name": "Amortissement du mobilier de bureau", "is_group": 0, "account_type": "Accumulated Depreciation"},
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "SCF-29": {
                        "number": "SCF-29",
                        "name": "Pertes de valeur sur immobilisations",
                        "is_group": 1,
                        "children": {
                            "SCF-290": {"number": "SCF-290", "name": "Pertes de valeur sur immobilisations incorporelles", "is_group": 0},
                            "SCF-291": {"number": "SCF-291", "name": "Pertes de valeur sur immobilisations corporelles", "is_group": 0},
                            "SCF-296": {"number": "SCF-296", "name": "Pertes de valeur sur participations et créances rattachées", "is_group": 0},
                        }
                    }
                }
            },

            # --- CLASSE 3 : STOCKS ET EN-COURS ---
            "SCF-3": {
                "number": "SCF-3",
                "name": "Classe 3 : Comptes de stocks et en-cours",
                "is_group": 1,
                "account_type": "Stock",
                "children": {
                    "SCF-30": {
                        "number": "SCF-30",
                        "name": "Stocks de marchandises",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-300": {"number": "SCF-300", "name": "Marchandises générales en magasin", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-31": {
                        "number": "SCF-31",
                        "name": "Matières premières et fournitures",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-311": {"number": "SCF-311", "name": "Matières premières", "is_group": 0, "account_type": "Stock"},
                            "SCF-312": {"number": "SCF-312", "name": "Matières consommables", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-32": {
                        "number": "SCF-32",
                        "name": "Autres approvisionnements",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-321": {"number": "SCF-321", "name": "Matières consommables et petits outillages", "is_group": 0, "account_type": "Stock"},
                            "SCF-322": {"number": "SCF-322", "name": "Fournitures consommables", "is_group": 0, "account_type": "Stock"},
                            "SCF-326": {"number": "SCF-326", "name": "Emballages", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-33": {
                        "number": "SCF-33",
                        "name": "En-cours de production de biens",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-331": {"number": "SCF-331", "name": "Produits en cours", "is_group": 0, "account_type": "Stock"},
                            "SCF-335": {"number": "SCF-335", "name": "Travaux en cours", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-34": {
                        "number": "SCF-34",
                        "name": "En-cours de production de services",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-341": {"number": "SCF-341", "name": "Études en cours", "is_group": 0, "account_type": "Stock"},
                            "SCF-345": {"number": "SCF-345", "name": "Prestations de services en cours", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-35": {
                        "number": "SCF-35",
                        "name": "Stocks de produits",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-351": {"number": "SCF-351", "name": "Produits intermédiaires", "is_group": 0, "account_type": "Stock"},
                            "SCF-355": {"number": "SCF-355", "name": "Produits finis", "is_group": 0, "account_type": "Stock"},
                            "SCF-358": {"number": "SCF-358", "name": "Produits résiduels (déchets, rebuts)", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-37": {
                        "number": "SCF-37",
                        "name": "Stocks à l'extérieur (en route, en dépôt, consignation)",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-370": {"number": "SCF-370", "name": "Stocks en cours de route", "is_group": 0, "account_type": "Stock"},
                            "SCF-371": {"number": "SCF-371", "name": "Stocks en dépôt ou en consignation", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-38": {
                        "number": "SCF-38",
                        "name": "Achats stockés (Comptes transitoires)",
                        "is_group": 1,
                        "account_type": "Stock",
                        "children": {
                            "SCF-380": {"number": "SCF-380", "name": "Achats de marchandises stockées", "is_group": 0, "account_type": "Stock"},
                            "SCF-381": {"number": "SCF-381", "name": "Achats de matières premières stockées", "is_group": 0, "account_type": "Stock"},
                            "SCF-382": {"number": "SCF-382", "name": "Achats d'autres approvisionnements stockés", "is_group": 0, "account_type": "Stock"},
                        }
                    },
                    "SCF-39": {
                        "number": "SCF-39",
                        "name": "Pertes de valeur sur stocks et en-cours",
                        "is_group": 1,
                        "children": {
                            "SCF-390": {"number": "SCF-390", "name": "Pertes de valeur sur stocks de marchandises", "is_group": 0},
                            "SCF-391": {"number": "SCF-391", "name": "Pertes de valeur sur matières premières", "is_group": 0},
                            "SCF-395": {"number": "SCF-395", "name": "Pertes de valeur sur stocks de produits", "is_group": 0},
                        }
                    }
                }
            },

            # --- CLASSE 4 (ACTIF) : CRÉANCES & ACTIFS CIRCULANTS ---
            "SCF-4A": {
                "number": "SCF-4A",
                "name": "Classe 4 : Comptes de tiers (Créances et Actifs circulants)",
                "is_group": 1,
                "children": {
                    "SCF-409": {
                        "number": "SCF-409",
                        "name": "Fournisseurs débiteurs (avances versées)",
                        "is_group": 1,
                        "children": {
                            "SCF-4091": {"number": "SCF-4091", "name": "Fournisseurs - Avances et acomptes versés sur commandes", "is_group": 0},
                            "SCF-4096": {"number": "SCF-4096", "name": "Fournisseurs - Créances pour emballages à rendre", "is_group": 0},
                            "SCF-4098": {"number": "SCF-4098", "name": "Fournisseurs - RRR à obtenir et autres avoirs non parvenus", "is_group": 0},
                        }
                    },
                    "SCF-41": {
                        "number": "SCF-41",
                        "name": "Clients et comptes rattachés",
                        "is_group": 1,
                        "account_type": "Receivable",
                        "children": {
                            "SCF-411": {
                                "number": "SCF-411",
                                "name": "Clients ordinaires",
                                "is_group": 1,
                                "account_type": "Receivable",
                                "children": {
                                    "SCF-4111": {"number": "SCF-4111", "name": "Clients d'exploitation locaux", "is_group": 0, "account_type": "Receivable"},
                                    "SCF-4112": {"number": "SCF-4112", "name": "Clients étrangers (Exportation)", "is_group": 0, "account_type": "Receivable"},
                                    "SCF-4117": {"number": "SCF-4117", "name": "Clients - Retenues de garantie", "is_group": 0, "account_type": "Receivable"},
                                }
                            },
                            "SCF-413": {"number": "SCF-413", "name": "Clients - Effets à recevoir", "is_group": 0, "account_type": "Receivable"},
                            "SCF-416": {"number": "SCF-416", "name": "Clients douteux ou litigieux", "is_group": 0, "account_type": "Receivable"},
                            "SCF-417": {"number": "SCF-417", "name": "Créances sur travaux non encore facturables", "is_group": 0, "account_type": "Receivable"},
                            "SCF-418": {"number": "SCF-418", "name": "Clients - Produits non encore facturés (Factures à établir)", "is_group": 0, "account_type": "Receivable"},
                        }
                    },
                    "SCF-425": {
                        "number": "SCF-425",
                        "name": "Personnel - Avances et acomptes",
                        "is_group": 1,
                        "children": {
                            "SCF-4251": {"number": "SCF-4251", "name": "Avances et acomptes accordés au personnel", "is_group": 0},
                        }
                    },
                    "SCF-44A": {
                        "number": "SCF-44A",
                        "name": "État et collectivités publiques (Créances fiscales)",
                        "is_group": 1,
                        "account_type": "Tax",
                        "children": {
                            "SCF-4441": {"number": "SCF-4441", "name": "État - Acomptes IBS versés / Crédits d'impôt", "is_group": 0, "account_type": "Tax"},
                            "SCF-4456": {
                                "number": "SCF-4456",
                                "name": "TVA déductible (récupérable)",
                                "is_group": 1,
                                "account_type": "Tax",
                                "children": {
                                    "SCF-44561": {"number": "SCF-44561", "name": "TVA déductible sur immobilisations", "is_group": 0, "account_type": "Tax"},
                                    "SCF-44562": {"number": "SCF-44562", "name": "TVA déductible sur biens et services (achats)", "is_group": 0, "account_type": "Tax"},
                                    "SCF-44567": {"number": "SCF-44567", "name": "Crédit de TVA à reporter", "is_group": 0, "account_type": "Tax"},
                                }
                            }
                        }
                    },
                    "SCF-46A": {
                        "number": "SCF-46A",
                        "name": "Débiteurs divers (Créances)",
                        "is_group": 1,
                        "children": {
                            "SCF-467": {"number": "SCF-467", "name": "Autres comptes débiteurs (créances diverses)", "is_group": 0},
                        }
                    },
                    "SCF-48A": {
                        "number": "SCF-48A",
                        "name": "Comptes de régularisation - Actif",
                        "is_group": 1,
                        "children": {
                            "SCF-486": {"number": "SCF-486", "name": "Charges constatées d'avance", "is_group": 0},
                            "SCF-489": {"number": "SCF-489", "name": "Écarts de conversion - Actif (pertes de change latentes)", "is_group": 0},
                        }
                    },
                    "SCF-49": {
                        "number": "SCF-49",
                        "name": "Pertes de valeur sur comptes de tiers",
                        "is_group": 1,
                        "children": {
                            "SCF-491": {"number": "SCF-491", "name": "Pertes de valeur sur créances clients", "is_group": 0},
                            "SCF-496": {"number": "SCF-496", "name": "Pertes de valeur sur débiteurs divers", "is_group": 0},
                        }
                    }
                }
            },

            # --- CLASSE 5 (ACTIF) : TRÉSORERIE ACTIVE (DISPONIBILITÉS) ---
            "SCF-5A": {
                "number": "SCF-5A",
                "name": "Classe 5 : Comptes financiers (Disponibilités et Trésorerie active)",
                "is_group": 1,
                "children": {
                    "SCF-50": {
                        "number": "SCF-50",
                        "name": "Valeurs mobilières de placement (VMP)",
                        "is_group": 1,
                        "children": {
                            "SCF-503": {"number": "SCF-503", "name": "Actions cotées (VMP)", "is_group": 0},
                            "SCF-506": {"number": "SCF-506", "name": "Obligations et bons du Trésor à court terme", "is_group": 0},
                            "SCF-508": {"number": "SCF-508", "name": "Autres valeurs mobilières de placement", "is_group": 0},
                        }
                    },
                    "SCF-51A": {
                        "number": "SCF-51A",
                        "name": "Banques, établissements financiers et assimilés",
                        "is_group": 1,
                        "account_type": "Bank",
                        "children": {
                            "SCF-512": {
                                "number": "SCF-512",
                                "name": "Banques commerciales (comptes courants)",
                                "is_group": 1,
                                "account_type": "Bank",
                                "children": {
                                    "SCF-5121": {"number": "SCF-5121", "name": "Banque Nationale d'Algérie (BNA)", "is_group": 0, "account_type": "Bank"},
                                    "SCF-5122": {"number": "SCF-5122", "name": "Banque de Développement Local (BDL)", "is_group": 0, "account_type": "Bank"},
                                    "SCF-5123": {"number": "SCF-5123", "name": "Banque Extérieure d'Algérie (BEA)", "is_group": 0, "account_type": "Bank"},
                                    "SCF-5124": {"number": "SCF-5124", "name": "Al Salam Bank Algeria", "is_group": 0, "account_type": "Bank"},
                                    "SCF-5128": {"number": "SCF-5128", "name": "Autres banques locales DZD", "is_group": 0, "account_type": "Bank"},
                                    "SCF-5129": {"number": "SCF-5129", "name": "Comptes bancaires en devises étrangères", "is_group": 0, "account_type": "Bank"},
                                }
                            },
                            "SCF-515": {"number": "SCF-515", "name": "Trésor public et Centre de Chèques Postaux (CCP)", "is_group": 0, "account_type": "Bank"},
                        }
                    },
                    "SCF-53": {
                        "number": "SCF-53",
                        "name": "Caisse (Espèces)",
                        "is_group": 1,
                        "account_type": "Cash",
                        "children": {
                            "SCF-531": {"number": "SCF-531", "name": "Caisse principale (Siège social)", "is_group": 0, "account_type": "Cash"},
                            "SCF-532": {"number": "SCF-532", "name": "Caisses secondaires et annexes", "is_group": 0, "account_type": "Cash"},
                        }
                    },
                    "SCF-54": {
                        "number": "SCF-54",
                        "name": "Régies d'avances et accréditifs",
                        "is_group": 1,
                        "children": {
                            "SCF-541": {"number": "SCF-541", "name": "Régies d'avances", "is_group": 0},
                            "SCF-542": {"number": "SCF-542", "name": "Accréditifs ouverts", "is_group": 0},
                        }
                    },
                    "SCF-58": {
                        "number": "SCF-58",
                        "name": "Virements internes de fonds",
                        "is_group": 1,
                        "children": {
                            "SCF-581": {"number": "SCF-581", "name": "Virements internes (Banque/Caisse/Compte à compte)", "is_group": 0},
                        }
                    },
                    "SCF-59": {
                        "number": "SCF-59",
                        "name": "Pertes de valeur sur actifs financiers courants",
                        "is_group": 1,
                        "children": {
                            "SCF-591": {"number": "SCF-591", "name": "Pertes de valeur sur valeurs mobilières de placement", "is_group": 0},
                        }
                    }
                }
            }
        }
    },

    # -------------------------------------------------------------------------
    # 2. PASSIF - DETTES (Root: Liability, Report: Balance Sheet)
    # Parent: 2000 - Source of Funds (Liabilities) - BSN
    # -------------------------------------------------------------------------
    "PASSIF": {
        "number": "SCF-PASSIF",
        "name": "SCF - Plan Comptable Financier (Passif - Dettes)",
        "root_type": "Liability",
        "report_type": "Balance Sheet",
        "is_group": 1,
        "children": {
            # --- CLASSE 1 (DETTES NON COURANTES) ---
            "SCF-1P": {
                "number": "SCF-1P",
                "name": "Classe 1 : Emprunts et dettes financières assimilées",
                "is_group": 1,
                "children": {
                    "SCF-15": {
                        "number": "SCF-15",
                        "name": "Provisions pour charges - Passifs non courants",
                        "is_group": 1,
                        "children": {
                            "SCF-153": {"number": "SCF-153", "name": "Provisions pour pensions et obligations similaires", "is_group": 0},
                            "SCF-155": {"number": "SCF-155", "name": "Provisions pour impôts futurs", "is_group": 0},
                            "SCF-158": {"number": "SCF-158", "name": "Autres provisions pour charges non courantes", "is_group": 0},
                        }
                    },
                    "SCF-16": {
                        "number": "SCF-16",
                        "name": "Emprunts et dettes assimilées",
                        "is_group": 1,
                        "children": {
                            "SCF-161": {"number": "SCF-161", "name": "Titres participatifs", "is_group": 0},
                            "SCF-164": {"number": "SCF-164", "name": "Emprunts auprès des établissements de crédit", "is_group": 0},
                            "SCF-167": {"number": "SCF-167", "name": "Dettes sur contrats de crédit-bail / location-financement", "is_group": 0},
                            "SCF-168": {"number": "SCF-168", "name": "Autres emprunts et dettes financières", "is_group": 0},
                        }
                    },
                    "SCF-17": {
                        "number": "SCF-17",
                        "name": "Dettes rattachées à des participations",
                        "is_group": 1,
                        "children": {
                            "SCF-171": {"number": "SCF-171", "name": "Dettes rattachées à des participations (groupe)", "is_group": 0},
                        }
                    },
                    "SCF-18": {
                        "number": "SCF-18",
                        "name": "Comptes de liaison des établissements et sociétés en participation",
                        "is_group": 1,
                        "children": {
                            "SCF-181": {"number": "SCF-181", "name": "Comptes de liaison des établissements", "is_group": 0},
                        }
                    }
                }
            },

            # --- CLASSE 4 (DETTES COURANTES) : FOURNISSEURS, PERSONNEL, ÉTAT ---
            "SCF-4P": {
                "number": "SCF-4P",
                "name": "Classe 4 : Comptes de tiers (Dettes fournisseurs, fiscales et sociales)",
                "is_group": 1,
                "children": {
                    "SCF-40": {
                        "number": "SCF-40",
                        "name": "Fournisseurs et comptes rattachés",
                        "is_group": 1,
                        "account_type": "Payable",
                        "children": {
                            "SCF-401": {
                                "number": "SCF-401",
                                "name": "Fournisseurs de biens et services",
                                "is_group": 1,
                                "account_type": "Payable",
                                "children": {
                                    "SCF-4011": {"number": "SCF-4011", "name": "Fournisseurs d'exploitation locaux", "is_group": 0, "account_type": "Payable"},
                                    "SCF-4012": {"number": "SCF-4012", "name": "Fournisseurs étrangers (Importation)", "is_group": 0, "account_type": "Payable"},
                                    "SCF-4017": {"number": "SCF-4017", "name": "Fournisseurs - Retenues de garantie subies", "is_group": 0, "account_type": "Payable"},
                                }
                            },
                            "SCF-403": {"number": "SCF-403", "name": "Fournisseurs - Effets à payer", "is_group": 0, "account_type": "Payable"},
                            "SCF-404": {"number": "SCF-404", "name": "Fournisseurs d'immobilisations", "is_group": 0, "account_type": "Payable"},
                            "SCF-408": {"number": "SCF-408", "name": "Fournisseurs - Factures non parvenues (FNP)", "is_group": 0, "account_type": "Payable"},
                        }
                    },
                    "SCF-419": {
                        "number": "SCF-419",
                        "name": "Clients créditeurs (avances reçues)",
                        "is_group": 1,
                        "children": {
                            "SCF-4191": {"number": "SCF-4191", "name": "Clients - Avances et acomptes reçus sur commandes", "is_group": 0},
                            "SCF-4196": {"number": "SCF-4196", "name": "Clients - Dettes pour emballages consignés", "is_group": 0},
                        }
                    },
                    "SCF-42P": {
                        "number": "SCF-42P",
                        "name": "Personnel et comptes rattachés (Dettes)",
                        "is_group": 1,
                        "children": {
                            "SCF-421": {"number": "SCF-421", "name": "Personnel - Rémunérations dues (salaires nets à payer)", "is_group": 0},
                            "SCF-422": {"number": "SCF-422", "name": "Comités d'entreprise et œuvres sociales dues", "is_group": 0},
                            "SCF-428": {"number": "SCF-428", "name": "Personnel - Charges à payer et provisions pour congés payés", "is_group": 0},
                        }
                    },
                    "SCF-43P": {
                        "number": "SCF-43P",
                        "name": "Sécurité sociale et autres organismes sociaux (Dettes)",
                        "is_group": 1,
                        "children": {
                            "SCF-431": {"number": "SCF-431", "name": "Sécurité sociale (CNAS à payer)", "is_group": 0},
                            "SCF-432": {"number": "SCF-432", "name": "Autres organismes sociaux (CASNOS, CACOBATPH)", "is_group": 0},
                            "SCF-438": {"number": "SCF-438", "name": "Organismes sociaux - Charges à payer", "is_group": 0},
                        }
                    },
                    "SCF-44P": {
                        "number": "SCF-44P",
                        "name": "État et collectivités publiques (Dettes fiscales)",
                        "is_group": 1,
                        "account_type": "Tax",
                        "children": {
                            "SCF-442": {"number": "SCF-442", "name": "État - Impôts et taxes recouvrables sur des tiers (IRG retenu à la source)", "is_group": 0, "account_type": "Tax"},
                            "SCF-444": {"number": "SCF-444", "name": "État - Impôts sur les bénéfices (IBS restant dû)", "is_group": 0, "account_type": "Tax"},
                            "SCF-445P": {
                                "number": "SCF-445P",
                                "name": "État - Taxes sur le chiffre d'affaires",
                                "is_group": 1,
                                "account_type": "Tax",
                                "children": {
                                    "SCF-4457": {"number": "SCF-4457", "name": "TVA collectée (facturée sur ventes)", "is_group": 0, "account_type": "Tax"},
                                    "SCF-4458": {"number": "SCF-4458", "name": "Taxes sur le chiffre d'affaires à régulariser", "is_group": 0, "account_type": "Tax"},
                                }
                            },
                            "SCF-447": {"number": "SCF-447", "name": "Autres impôts et taxes (TAP due, taxe d'apprentissage)", "is_group": 0, "account_type": "Tax"},
                            "SCF-448": {"number": "SCF-448", "name": "État - Charges à payer (provisions pour impôts)", "is_group": 0, "account_type": "Tax"},
                        }
                    },
                    "SCF-45": {
                        "number": "SCF-45",
                        "name": "Groupe et associés (Dettes)",
                        "is_group": 1,
                        "children": {
                            "SCF-455": {"number": "SCF-455", "name": "Associés - Comptes courants d'associés", "is_group": 0},
                            "SCF-457": {"number": "SCF-457", "name": "Associés - Dividendes à payer", "is_group": 0},
                        }
                    },
                    "SCF-46P": {
                        "number": "SCF-46P",
                        "name": "Créditeurs divers",
                        "is_group": 1,
                        "children": {
                            "SCF-468": {"number": "SCF-468", "name": "Autres comptes créditeurs (charges à payer diverses)", "is_group": 0},
                        }
                    },
                    "SCF-48P": {
                        "number": "SCF-48P",
                        "name": "Comptes de régularisation - Passif",
                        "is_group": 1,
                        "children": {
                            "SCF-487": {"number": "SCF-487", "name": "Produits constatés d'avance", "is_group": 0},
                            "SCF-488": {"number": "SCF-488", "name": "Écarts de conversion - Passif (gains de change latents)", "is_group": 0},
                        }
                    }
                }
            },

            # --- CLASSE 5 (PASSIF) : TRÉSORERIE PASSIVE ---
            "SCF-5P": {
                "number": "SCF-5P",
                "name": "Classe 5 : Trésorerie passive (Concours bancaires courants)",
                "is_group": 1,
                "children": {
                    "SCF-519": {
                        "number": "SCF-519",
                        "name": "Concours bancaires courants et crédits de trésorerie",
                        "is_group": 1,
                        "children": {
                            "SCF-5191": {"number": "SCF-5191", "name": "Découverts bancaires autorisés", "is_group": 0},
                            "SCF-5192": {"number": "SCF-5192", "name": "Crédits de trésorerie à court terme", "is_group": 0},
                        }
                    }
                }
            }
        }
    },

    # -------------------------------------------------------------------------
    # 3. CAPITAUX PROPRES (Root: Equity, Report: Balance Sheet)
    # Parent: 3000 - Equity - BSN
    # -------------------------------------------------------------------------
    "EQUITY": {
        "number": "SCF-EQUITY",
        "name": "SCF - Plan Comptable Financier (Capitaux Propres)",
        "root_type": "Equity",
        "report_type": "Balance Sheet",
        "is_group": 1,
        "children": {
            "SCF-1E": {
                "number": "SCF-1E",
                "name": "Classe 1 : Comptes de capitaux propres (Fonds propres)",
                "is_group": 1,
                "children": {
                    "SCF-10": {
                        "number": "SCF-10",
                        "name": "Capital, réserves et primes",
                        "is_group": 1,
                        "children": {
                            "SCF-101": {
                                "number": "SCF-101",
                                "name": "Capital émis (capital social ou fonds de dotation)",
                                "is_group": 1,
                                "children": {
                                    "SCF-1011": {"number": "SCF-1011", "name": "Capital souscrit, non appelé", "is_group": 0},
                                    "SCF-1012": {"number": "SCF-1012", "name": "Capital souscrit, appelé, non versé", "is_group": 0},
                                    "SCF-1013": {"number": "SCF-1013", "name": "Capital souscrit, appelé, versé", "is_group": 0},
                                }
                            },
                            "SCF-103": {"number": "SCF-103", "name": "Primes liées au capital social", "is_group": 0},
                            "SCF-104": {"number": "SCF-104", "name": "Écarts d'évaluation", "is_group": 0},
                            "SCF-105": {"number": "SCF-105", "name": "Écarts de réévaluation", "is_group": 0},
                            "SCF-106": {
                                "number": "SCF-106",
                                "name": "Réserves",
                                "is_group": 1,
                                "children": {
                                    "SCF-1061": {"number": "SCF-1061", "name": "Réserve légale", "is_group": 0},
                                    "SCF-1062": {"number": "SCF-1062", "name": "Réserves statutaires", "is_group": 0},
                                    "SCF-1063": {"number": "SCF-1063", "name": "Réserves réglementées", "is_group": 0},
                                    "SCF-1068": {"number": "SCF-1068", "name": "Autres réserves", "is_group": 0},
                                }
                            },
                            "SCF-108": {"number": "SCF-108", "name": "Compte de l'exploitant individuel", "is_group": 0},
                        }
                    },
                    "SCF-11": {
                        "number": "SCF-11",
                        "name": "Report à nouveau",
                        "is_group": 1,
                        "children": {
                            "SCF-110": {"number": "SCF-110", "name": "Report à nouveau (solde créditeur)", "is_group": 0},
                            "SCF-119": {"number": "SCF-119", "name": "Report à nouveau (solde débiteur)", "is_group": 0},
                        }
                    },
                    "SCF-12": {
                        "number": "SCF-12",
                        "name": "Résultat de l'exercice",
                        "is_group": 1,
                        "children": {
                            "SCF-120": {"number": "SCF-120", "name": "Résultat net de l'exercice (Bénéfice)", "is_group": 0},
                            "SCF-129": {"number": "SCF-129", "name": "Résultat net de l'exercice (Perte)", "is_group": 0},
                        }
                    },
                    "SCF-13": {
                        "number": "SCF-13",
                        "name": "Produits et charges différés (Subventions)",
                        "is_group": 1,
                        "children": {
                            "SCF-131": {"number": "SCF-131", "name": "Subventions d'équipement", "is_group": 0},
                            "SCF-132": {"number": "SCF-132", "name": "Autres subventions d'investissement", "is_group": 0},
                        }
                    }
                }
            }
        }
    },

    # -------------------------------------------------------------------------
    # 4. CHARGES (Root: Expense, Report: Profit and Loss)
    # Parent: 5000 - Expenses - BSN
    # -------------------------------------------------------------------------
    "CHARGES": {
        "number": "SCF-CHARGES",
        "name": "SCF - Plan Comptable Financier (Charges)",
        "root_type": "Expense",
        "report_type": "Profit and Loss",
        "is_group": 1,
        "children": {
            "SCF-6": {
                "number": "SCF-6",
                "name": "Classe 6 : Comptes de charges",
                "is_group": 1,
                "children": {
                    "SCF-60": {
                        "number": "SCF-60",
                        "name": "Achats consommés",
                        "is_group": 1,
                        "children": {
                            "SCF-600": {"number": "SCF-600", "name": "Achats de marchandises vendues", "is_group": 0, "account_type": "Cost of Goods Sold"},
                            "SCF-601": {"number": "SCF-601", "name": "Matières premières consommées", "is_group": 0, "account_type": "Cost of Goods Sold"},
                            "SCF-602": {"number": "SCF-602", "name": "Autres approvisionnements consommés", "is_group": 0},
                            "SCF-603": {"number": "SCF-603", "name": "Variations des stocks d'approvisionnements et marchandises", "is_group": 0, "account_type": "Stock Adjustment"},
                            "SCF-604": {"number": "SCF-604", "name": "Achats d'études et prestations de services", "is_group": 0},
                            "SCF-605": {"number": "SCF-605", "name": "Achats de matériel, équipements et travaux", "is_group": 0},
                            "SCF-607": {"number": "SCF-607", "name": "Achats non stockés de matières et fournitures", "is_group": 0},
                            "SCF-608": {"number": "SCF-608", "name": "Frais accessoires sur achats (transport, douane)", "is_group": 0},
                            "SCF-609": {"number": "SCF-609", "name": "Rabais, remises, ristournes obtenus sur achats", "is_group": 0},
                        }
                    },
                    "SCF-61": {
                        "number": "SCF-61",
                        "name": "Services extérieurs",
                        "is_group": 1,
                        "children": {
                            "SCF-611": {"number": "SCF-611", "name": "Sous-traitance générale", "is_group": 0},
                            "SCF-613": {"number": "SCF-613", "name": "Locations immobilières et mobilières", "is_group": 0},
                            "SCF-614": {"number": "SCF-614", "name": "Charges locatives et de copropriété", "is_group": 0},
                            "SCF-615": {"number": "SCF-615", "name": "Entretien, réparations et maintenance", "is_group": 0},
                            "SCF-616": {"number": "SCF-616", "name": "Primes d'assurances", "is_group": 0},
                            "SCF-617": {"number": "SCF-617", "name": "Études et recherches externes", "is_group": 0},
                            "SCF-618": {"number": "SCF-618", "name": "Divers services extérieurs", "is_group": 0},
                            "SCF-619": {"number": "SCF-619", "name": "Rabais, remises et ristournes obtenus sur services extérieurs", "is_group": 0},
                        }
                    },
                    "SCF-62": {
                        "number": "SCF-62",
                        "name": "Autres services extérieurs",
                        "is_group": 1,
                        "children": {
                            "SCF-621": {"number": "SCF-621", "name": "Personnel extérieur à l'entreprise (intérim)", "is_group": 0},
                            "SCF-622": {"number": "SCF-622", "name": "Rémunérations d'intermédiaires et honoraires (experts, juristes, auditeurs)", "is_group": 0},
                            "SCF-623": {"number": "SCF-623", "name": "Publicité, publications, relations publiques", "is_group": 0},
                            "SCF-624": {"number": "SCF-624", "name": "Transports de biens et transport collectif du personnel", "is_group": 0},
                            "SCF-625": {"number": "SCF-625", "name": "Déplacements, missions et réceptions", "is_group": 0},
                            "SCF-626": {"number": "SCF-626", "name": "Frais postaux et de télécommunications (téléphone, internet)", "is_group": 0},
                            "SCF-627": {"number": "SCF-627", "name": "Services bancaires et assimilés (frais bancaires)", "is_group": 0},
                            "SCF-628": {"number": "SCF-628", "name": "Cotisations professionnelles et divers", "is_group": 0},
                            "SCF-629": {"number": "SCF-629", "name": "Rabais, remises et ristournes obtenus sur autres services extérieurs", "is_group": 0},
                        }
                    },
                    "SCF-63": {
                        "number": "SCF-63",
                        "name": "Charges de personnel",
                        "is_group": 1,
                        "children": {
                            "SCF-631": {"number": "SCF-631", "name": "Rémunérations du personnel (salaires, primes, heures supp)", "is_group": 0},
                            "SCF-634": {"number": "SCF-634", "name": "Rémunération de l'exploitant individuel", "is_group": 0},
                            "SCF-635": {"number": "SCF-635", "name": "Cotisations aux organismes sociaux (CNAS part patronale)", "is_group": 0},
                            "SCF-636": {"number": "SCF-636", "name": "Charges sociales de l'exploitant individuel (CASNOS)", "is_group": 0},
                            "SCF-637": {"number": "SCF-637", "name": "Autres charges sociales et médecine du travail", "is_group": 0},
                            "SCF-638": {"number": "SCF-638", "name": "Charges de personnel diverses", "is_group": 0},
                        }
                    },
                    "SCF-64": {
                        "number": "SCF-64",
                        "name": "Impôts, taxes et versements assimilés",
                        "is_group": 1,
                        "account_type": "Tax",
                        "children": {
                            "SCF-641": {"number": "SCF-641", "name": "Impôts et taxes directs (TAP - Taxe sur l'activité professionnelle)", "is_group": 0, "account_type": "Tax"},
                            "SCF-642": {"number": "SCF-642", "name": "Taxes sur le chiffre d'affaires non récupérables", "is_group": 0, "account_type": "Tax"},
                            "SCF-645": {"number": "SCF-645", "name": "Autres impôts et taxes (droits de timbre, taxes locales)", "is_group": 0, "account_type": "Tax"},
                        }
                    },
                    "SCF-65": {
                        "number": "SCF-65",
                        "name": "Autres charges de gestion courante",
                        "is_group": 1,
                        "children": {
                            "SCF-651": {"number": "SCF-651", "name": "Redevances pour concessions, brevets, licences", "is_group": 0},
                            "SCF-652": {"number": "SCF-652", "name": "Moins-values sur cessions d'actifs courants", "is_group": 0},
                            "SCF-654": {"number": "SCF-654", "name": "Pertes sur créances irrécouvrables", "is_group": 0},
                            "SCF-656": {"number": "SCF-656", "name": "Amendes et pénalités, subventions accordées, dons", "is_group": 0},
                            "SCF-657": {"number": "SCF-657", "name": "Charges exceptionnelles de gestion courante", "is_group": 0},
                            "SCF-658": {"number": "SCF-658", "name": "Charges diverses de gestion courante", "is_group": 0},
                        }
                    },
                    "SCF-66": {
                        "number": "SCF-66",
                        "name": "Charges financières",
                        "is_group": 1,
                        "children": {
                            "SCF-661": {"number": "SCF-661", "name": "Charges d'intérêts bancaires et financiers", "is_group": 0},
                            "SCF-665": {"number": "SCF-665", "name": "Pertes de change", "is_group": 0},
                            "SCF-668": {"number": "SCF-668", "name": "Autres charges financières (escomptes accordés)", "is_group": 0},
                        }
                    },
                    "SCF-67": {
                        "number": "SCF-67",
                        "name": "Éléments extraordinaires (Charges)",
                        "is_group": 1,
                        "children": {
                            "SCF-671": {"number": "SCF-671", "name": "Charges extraordinaires", "is_group": 0},
                        }
                    },
                    "SCF-68": {
                        "number": "SCF-68",
                        "name": "Dotations aux amortissements, provisions et pertes de valeur",
                        "is_group": 1,
                        "account_type": "Depreciation",
                        "children": {
                            "SCF-681": {"number": "SCF-681", "name": "Dotations aux amortissements et pertes de valeur - Actifs non courants", "is_group": 0, "account_type": "Depreciation"},
                            "SCF-685": {"number": "SCF-685", "name": "Dotations aux provisions d'exploitation", "is_group": 0},
                            "SCF-686": {"number": "SCF-686", "name": "Dotations financières aux amortissements et provisions", "is_group": 0},
                        }
                    },
                    "SCF-69": {
                        "number": "SCF-69",
                        "name": "Impôts sur les bénéfices et assimilés",
                        "is_group": 1,
                        "account_type": "Tax",
                        "children": {
                            "SCF-695": {"number": "SCF-695", "name": "Impôts sur les bénéfices basés sur le résultat (IBS)", "is_group": 0, "account_type": "Tax"},
                            "SCF-698": {"number": "SCF-698", "name": "Autres impôts sur les résultats", "is_group": 0, "account_type": "Tax"},
                        }
                    }
                }
            }
        }
    },

    # -------------------------------------------------------------------------
    # 5. PRODUITS (Root: Income, Report: Profit and Loss)
    # Parent: 4000 - Income - BSN
    # -------------------------------------------------------------------------
    "PRODUITS": {
        "number": "SCF-PRODUITS",
        "name": "SCF - Plan Comptable Financier (Produits)",
        "root_type": "Income",
        "report_type": "Profit and Loss",
        "is_group": 1,
        "children": {
            "SCF-7": {
                "number": "SCF-7",
                "name": "Classe 7 : Comptes de produits",
                "is_group": 1,
                "children": {
                    "SCF-70": {
                        "number": "SCF-70",
                        "name": "Ventes de marchandises et produits, prestations de services",
                        "is_group": 1,
                        "account_type": "Income Account",
                        "children": {
                            "SCF-700": {"number": "SCF-700", "name": "Ventes de marchandises", "is_group": 0, "account_type": "Income Account"},
                            "SCF-701": {"number": "SCF-701", "name": "Ventes de produits finis", "is_group": 0, "account_type": "Income Account"},
                            "SCF-702": {"number": "SCF-702", "name": "Ventes de produits intermédiaires", "is_group": 0, "account_type": "Income Account"},
                            "SCF-703": {"number": "SCF-703", "name": "Ventes de produits résiduels", "is_group": 0, "account_type": "Income Account"},
                            "SCF-704": {"number": "SCF-704", "name": "Travaux d'installation et de chantiers", "is_group": 0, "account_type": "Income Account"},
                            "SCF-705": {"number": "SCF-705", "name": "Études et conseils facturés", "is_group": 0, "account_type": "Income Account"},
                            "SCF-706": {"number": "SCF-706", "name": "Prestations de services et maintenance", "is_group": 0, "account_type": "Income Account"},
                            "SCF-708": {"number": "SCF-708", "name": "Produits des activités annexes (ports facturés)", "is_group": 0, "account_type": "Income Account"},
                            "SCF-709": {"number": "SCF-709", "name": "Rabais, remises et ristournes accordés sur ventes", "is_group": 0, "account_type": "Income Account"},
                        }
                    },
                    "SCF-72": {
                        "number": "SCF-72",
                        "name": "Production stockée ou déstockée",
                        "is_group": 1,
                        "children": {
                            "SCF-723": {"number": "SCF-723", "name": "Variation des stocks d'en-cours", "is_group": 0},
                            "SCF-724": {"number": "SCF-724", "name": "Variation des stocks de produits", "is_group": 0},
                        }
                    },
                    "SCF-73": {
                        "number": "SCF-73",
                        "name": "Production immobilisée",
                        "is_group": 1,
                        "children": {
                            "SCF-731": {"number": "SCF-731", "name": "Production immobilisée - Actifs incorporels (logiciels)", "is_group": 0},
                            "SCF-732": {"number": "SCF-732", "name": "Production immobilisée - Actifs corporels", "is_group": 0},
                        }
                    },
                    "SCF-74": {
                        "number": "SCF-74",
                        "name": "Subventions d'exploitation",
                        "is_group": 1,
                        "children": {
                            "SCF-741": {"number": "SCF-741", "name": "Subvention d'équilibre", "is_group": 0},
                            "SCF-748": {"number": "SCF-748", "name": "Autres subventions d'exploitation", "is_group": 0},
                        }
                    },
                    "SCF-75": {
                        "number": "SCF-75",
                        "name": "Autres produits de gestion courante",
                        "is_group": 1,
                        "children": {
                            "SCF-751": {"number": "SCF-751", "name": "Redevances pour concessions, brevets, licences", "is_group": 0},
                            "SCF-752": {"number": "SCF-752", "name": "Plus-values de cession d'actifs courants", "is_group": 0},
                            "SCF-754": {"number": "SCF-754", "name": "Rentrées sur créances amorties", "is_group": 0},
                            "SCF-758": {"number": "SCF-758", "name": "Produits divers de gestion courante", "is_group": 0},
                        }
                    },
                    "SCF-76": {
                        "number": "SCF-76",
                        "name": "Produits financiers",
                        "is_group": 1,
                        "children": {
                            "SCF-761": {"number": "SCF-761", "name": "Produits de participations (dividendes)", "is_group": 0},
                            "SCF-762": {"number": "SCF-762", "name": "Revenus des autres immobilisations financières", "is_group": 0},
                            "SCF-765": {"number": "SCF-765", "name": "Gains de change", "is_group": 0},
                            "SCF-768": {"number": "SCF-768", "name": "Autres produits financiers (escomptes obtenus)", "is_group": 0},
                        }
                    },
                    "SCF-77": {
                        "number": "SCF-77",
                        "name": "Éléments extraordinaires (Produits)",
                        "is_group": 1,
                        "children": {
                            "SCF-771": {"number": "SCF-771", "name": "Produits extraordinaires", "is_group": 0},
                        }
                    },
                    "SCF-78": {
                        "number": "SCF-78",
                        "name": "Reprises sur amortissements, pertes de valeur et provisions",
                        "is_group": 1,
                        "children": {
                            "SCF-781": {"number": "SCF-781", "name": "Reprises d'exploitation sur amortissements et pertes de valeur", "is_group": 0},
                            "SCF-785": {"number": "SCF-785", "name": "Reprises d'exploitation sur provisions", "is_group": 0},
                            "SCF-786": {"number": "SCF-786", "name": "Reprises financières", "is_group": 0},
                        }
                    }
                }
            }
        }
    }
}
