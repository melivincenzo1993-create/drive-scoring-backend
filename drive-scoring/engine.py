from datetime import date
import schemas

def calcola_score_privato(dati: schemas.PrivatoRequest) -> dict:
    # Si parte da un punteggio base di 100
    score = 100.0
    penalizzazioni = []
    
    # -----------------------------------------------------------------
    # 1. RAPPORTO RATA/REDDITO (DTI - Debt-to-Income)
    # -----------------------------------------------------------------
    # Rata totale mensile = Nuova rata stimata + Debiti mensili correnti
    rata_totale = dati.estimated_monthly_rate + dati.current_monthly_debts
    reddito = dati.net_monthly_income
    
    if reddito <= 0:
        return {"score": 0, "status": "BOCCIATO", "motivo": "Reddito non valido"}
        
    dti = (rata_totale / reddito) * 100
    
    if dti <= 30:
        # Ottimo, nessuna penalizzazione
        pass
    elif 30 < dti <= 40:
        score -= 15
        penalizzazioni.append("Rapporto rata/reddito moderato (30-40%)")
    elif 40 < dti <= 50:
        score -= 35
        penalizzazioni.append("Rapporto rata/reddito elevato (40-50%)")
    else:  # dti > 50%
        score -= 60
        penalizzazioni.append("Rapporto rata/reddito critico (>50%)")

    # -----------------------------------------------------------------
    # 2. REDDITO RESIDUO (Sostenibilità della vita)
    # -----------------------------------------------------------------
    reddito_residuo = reddito - rata_totale
    if reddito_residuo < 700:
        score -= 20
        penalizzazioni.append("Reddito residuo mensile sotto la soglia minima di sussistenza")
    elif reddito_residuo < 1000:
        score -= 10
        penalizzazioni.append("Reddito residuo mensile al limite della soglia di sicurezza")

    # -----------------------------------------------------------------
    # 3. TIPOLOGIA DI CONTRATTO E SETTORE AZIENDALE
    # -----------------------------------------------------------------
    # Premiamo il tempo indeterminato e il pubblico
    if dati.contract_type == "INDETERMINATO":
        if dati.employer_sector == "PUBBLICO":
            # Massimo della stabilità, nessun malus
            pass
        elif dati.employer_sector == "PRIVATO_SPA_SRL":
            score -= 5  # Rischio ditta privata minimo
        else:  # PRIVATO_MINORE
            score -= 10
            penalizzazioni.append("Dipendente di azienda privata minore")
    elif dati.contract_type == "DETERMINATO":
        score -= 25
        penalizzazioni.append("Contratto di lavoro a tempo determinato")
    elif dati.contract_type == "APPRENDISTATO":
        score -= 15
        penalizzazioni.append("Contratto di apprendistato")

    # -----------------------------------------------------------------
    # 4. ANZIANITÀ LAVORATIVA
    # -----------------------------------------------------------------
    oggi = date.today()
    # Calcolo approssimativo degli anni di servizio
    anni_servizio = (oggi - dati.employment_start_date).days / 365.25
    
    if anni_servizio < 1.0:
        score -= 15
        penalizzazioni.append("Anzianità lavorativa inferiore a 1 anno (periodo di prova/rischio di轉)")
    elif anni_servizio < 3.0:
        score -= 5
        # Anzianità discreta

    # -----------------------------------------------------------------
    # 5. STORICO CREDITIZIO (Il blocco vincolante)
    # -----------------------------------------------------------------
    if dati.has_credit_issues:
        score -= 50
        penalizzazioni.append("Presenza di segnalazioni o ritardi nei pagamenti (CRIF/Pregiudizievoli)")

    # -----------------------------------------------------------------
    # CALCOLO FINALE DELLO STATO
    # -----------------------------------------------------------------
    # Assicuriamoci che lo score non vada sotto lo 0 o sopra i 100
    score = max(0.0, min(100.0, score))
    
    if score >= 75:
        status = "APPROVATO"
    elif 60 <= score < 75:
        status = "DA_REVISIONARE"  # Pratica borderline, richiede istruttoria manuale
    else:
        status = "BOCCIATO"
        
    return {
        "score": int(score),
        "status": status,
        "dti_percentage": round(dti, 2),
        "reddito_residuo": round(reddito_residuo, 2),
        "note": penalizzazioni if penalizzazioni else ["Profilo finanziario eccellente"]
    }
