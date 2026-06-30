from datetime import date

def calcola_scoring(dati: dict) -> dict:
    """
    Core Engine di Drive Scoring.
    Prende in input un dizionario di dati validati e restituisce:
    - score (1-100)
    - classe (A, B, C, D)
    - ko_reason (se presente)
    - sub_scores (dettaglio dei punteggi parziali)
    """
    
    # ---------------------------------------------------------
    # 1. CONTROLLI BLOCCANTI (HARD K.O.)
    # ---------------------------------------------------------
    
    # K.O. per segnalazioni gravi autodichiarate
    if dati.get("has_credit_issues") is True:
        return {
            "score": 0, "classe": "D", 
            "ko_reason": "Presenza di segnalazioni o anomalie creditizie attive.",
            "sub_scores": {"storico": 0, "sostenibilita": 0, "stabilita": 0, "anagrafica": 0}
        }

    # Calcolo della rata e del reddito disponibile per il Rapporto Rata/Reddito
    rata = dati.get("estimated_monthly_rate", 0)
    altre_rate = dati.get("current_monthly_debts", 0)
    profilo = dati.get("target_profile")
    
    # Estraiamo il reddito mensile in base al profilo
    if profilo == "PRIVATO":
        reddito_netto = dati.get("net_monthly_income", 0)
    elif profilo == "PENSIONATO":
        # Sottraiamo l'eventuale cessione del quinto già attiva sul cedolino
        reddito_netto = dati.get("net_monthly_pension", 0) - dati.get("assigned_fifth_amount", 0)
    elif profilo == "PROFESSIONISTA":
        # Per la P.IVA facciamo la media dell'utile netto mensile dell'ultimo anno
        reddito_netto = dati.get("net_profit_year_n1", 0) / 12
    else:
        reddito_netto = 0

    reddito_disponibile = reddito_netto - altre_rate

    # Protezione divisione per zero
    if reddito_disponibile <= 0:
        return {
            "score": 10, "classe": "D", 
            "ko_reason": "Il reddito netto disponibile è insufficiente o negativo.",
            "sub_scores": {"storico": 10, "sostenibilita": 10, "stabilita": 10, "anagrafica": 10}
        }

    # Calcolo effettivo del Rapporto Rata/Reddito
    rapporto_rata_reddito = (rata / reddito_disponibile) * 100

    # K.O. Tecnico se la rata mangia più del 50% del reddito disponibile
    if rapporto_rata_reddito > 50:
        return {
            "score": 20, "classe": "D", 
            "ko_reason": f"Sostenibilità insufficiente: la rata rappresenta il {round(rapporto_rata_reddito)}% del reddito disponibile (Max 50%).",
            "sub_scores": {"storico": 100, "sostenibilita": 10, "stabilita": 100, "anagrafica": 100}
        }

    # Controlli K.O. specifici per il profilo PENSIONATO (Età a fine contratto)
    oggi = date.today()
    if profilo == "PENSIONATO" and "birth_date" in dati:
        eta_attuale = oggi.year - dati["birth_date"].year
        durata_anni = dati.get("contract_duration_months", 0) / 12
        eta_fine_contratto = eta_attuale + durata_anni
        if eta_fine_contratto > 82:
            return {
                "score": 15, "classe": "D", 
                "ko_reason": f"Età a fine contratto ({round(eta_fine_contratto)} anni) superiore al limite massimo assicurativo di 82 anni.",
                "sub_scores": {"storico": 100, "sostenibilita": 100, "stabilita": 100, "anagrafica": 0}
            }

    # Controlli K.O. specifici per PROFESSIONISTA (Anzianità P.IVA inferiore a 12 mesi)
    if profilo == "PROFESSIONISTA" and "vat_start_date" in dati:
        mesi_attivita = (oggi - dati["vat_start_date"]).days / 30.4
        if mesi_attivita < 12:
            return {
                "score": 15, "classe": "D", 
                "ko_reason": "Anzianità di Partita IVA inferiore ai 12 mesi minimi richiesti dalle finanziarie.",
                "sub_scores": {"storico": 100, "sostenibilita": 100, "stabilita": 0, "anagrafica": 100}
            }

    # ---------------------------------------------------------
    # 2. ASSEGNAZIONE PUNTEGGI PARZIALI (Se i K.O. sono superati)
    # ---------------------------------------------------------
    sub_scores = {"storico": 100, "sostenibilita": 100, "stabilita": 100, "anagrafica": 100}

    # A. Sostenibilità (Rapporto Rata/Reddito) - Peso 40%
    if rapporto_rata_reddito <= 25:
        sub_scores["sostenibilita"] = 100
    elif rapporto_rata_reddito <= 35:
        sub_scores["sostenibilita"] = 85
    elif rapporto_rata_reddito <= 45:
        sub_scores["sostenibilita"] = 50
    else:
        sub_scores["sostenibilita"] = 25

    # B. Stabilità Lavorativa/Aziendale - Peso 40%
    if profilo == "PRIVATO":
        tipo_contratto = dati.get("contract_type")
        settore = dati.get("employer_sector")
        
        if tipo_contratto == "DETERMINATO" or tipo_contratto == "APPRENDISTATO":
            sub_scores["stabilita"] = 35
        elif settore == "PUBBLICO":
            sub_scores["stabilita"] = 100
        elif settore == "PRIVATO_SPA_SRL":
            sub_scores["stabilita"] = 85
        else: # Privato minore / ditte individuali
            sub_scores["stabilita"] = 65
            
    elif profilo == "PROFESSIONISTA":
        # Calcolo del trend basato sugli utili degli ultimi due anni
        utile_n1 = dati.get("net_profit_year_n1", 0)
        utile_n2 = dati.get("net_profit_year_n2", 0)
        if utile_n1 < utile_n2: # Trend decrescente
            sub_scores["stabilita"] = 50
        else:
            sub_scores["stabilita"] = 90
            
    elif profilo == "PENSIONATO":
        # Il pensionato ha la massima stabilità di reddito possibile
        sub_scores["stabilita"] = 100

    # C. Anagrafica ed Età - Peso 20%
    if profilo == "PENSIONATO" and "birth_date" in dati:
        eta_attuale = oggi.year - dati["birth_date"].year
        durata_anni = dati.get("contract_duration_months", 0) / 12
        if (eta_attuale + durata_anni) > 75:
            sub_scores["anagrafica"] = 60  # Malus progressivo

    # ---------------------------------------------------------
    # 3. CALCOLO BILANCIATO FINALE
    # ---------------------------------------------------------
    score_finale = int(
        (sub_scores["sostenibilita"] * 0.40) + 
        (sub_scores["stabilita"] * 0.40) + 
        (sub_scores["anagrafica"] * 0.20)
    )

    # Definizione delle Classi di Rischio
    if score_finale >= 85:
        classe = "A"
    elif score_finale >= 65:
        classe = "B"
    elif score_finale >= 45:
        classe = "C"
    else:
        classe = "D"

    return {
        "score": score_finale,
        "classe": classe,
        "ko_reason": None,
        "sub_scores": sub_scores
    }
    