from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from datetime import date

app = FastAPI(
    title="Drive Scoring API",
    description="Backend per il calcolo dell'indice di solvibilità finanziaria.",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Backend online! Vai su /docs per testare l'API."}

@app.post("/score/privato")
async def score_privato(
    user_email: str = Form(..., description="Email dell'utente"),
    target_profile: str = Form(..., description="Profilo di destinazione"),
    product_type: str = Form(..., description="Tipologia di prodotto richiesto"),
    contract_duration_months: int = Form(..., description="Durata del contratto in mesi"),
    estimated_monthly_rate: float = Form(..., description="Rata mensile stimata"),
    initial_down_payment: float = Form(..., description="Anticipo iniziale"),
    current_monthly_debts: float = Form(..., description="Debiti/rate mensili attuali"),
    has_credit_issues: bool = Form(..., description="Presenza di segnalazioni o insolvenze passate (True/False)"),
    birth_date: date = Form(..., description="Data di nascita (YYYY-MM-DD)"),
    contract_type: str = Form(..., description="Tipo di contratto lavorativo (es. indeterminato, determinato)"),
    employment_start_date: date = Form(..., description="Data inizio impiego (YYYY-MM-DD)"),
    employer_sector: str = Form(..., description="Settore lavorativo dell'azienda datrice"),
    net_monthly_income: float = Form(..., description="Reddito mensile netto"),
    documento_reddito: UploadFile = File(..., description="Carica il documento di reddito (PDF o Immagine)")
):
    # 1. Controllo estensione del documento caricato
    if not documento_reddito.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(
            status_code=400, 
            detail="Formato file non valido. Caricare esclusivamente un file PDF o un'immagine (PNG, JPG)."
        )

    # Legge il file in memoria (pronto per futuri salvataggi o analisi)
    contenuto_file = await documento_reddito.read()
    nome_documento = documento_reddito.filename

    # 2. Algoritmo di calcolo dello Credit Scoring (Base 100)
    punteggio = 100
    motivi_penalizzazione = []
    
    # Penalità per segnalazioni crif/insolvenze
    if has_credit_issues:
        punteggio -= 40
        motivi_penalizzazione.append("Presenza di segnalazioni o insolvenze creditizie.")
        
    # Penalità per contratti precari o non a tempo indeterminato
    if "indeterminato" not in contract_type.lower():
        punteggio -= 20
        motivi_penalizzazione.append("Contratto di lavoro non a tempo indeterminato.")
        
    # Calcolo dell'indice di indebitamento complessivo (Rata stimata + Debiti attuali)
    impegno_mensile_totale = estimated_monthly_rate + current_monthly_debts
    rapporto_indebitamento = impegno_mensile_totale / net_monthly_income if net_monthly_income > 0 else 1
    
    # Se le rate superano il 35% delle entrate, scatta il malus
    if rapporto_indebitamento > 0.35:
        punteggio -= 25
        motivi_penalizzazione.append("Rapporto rata/reddito troppo elevato (superiore al 35%).")

    # Controllo età (es. profili troppo giovani o in età pensionabile avanzata)
    oggi = date.today()
    eta_utente = oggi.year - birth_date.year - ((oggi.month, oggi.day) < (birth_date.month, birth_date.day))
    if eta_utente < 22 or eta_utente > 67:
        punteggio -= 10
        motivi_penalizzazione.append("Età fuori dalla fascia ottimale di finanziabilità.")

    # Assicuriamoci che lo score non scenda mai sotto lo 0
    punteggio_finale = max(0, punteggio)

    # 3. Determinazione dell'esito finale della pratica
    if punteggio_finale >= 70:
        esito = "APPROVATO"
    elif punteggio_finale >= 45:
        esito = "DA VERIFICARE (Richiede analisi manuale della busta paga)"
    else:
        esito = "RIFIUTATO"

    # 4. Risposta finale restituita all'interfaccia grafica
    return {
        "status": "success",
        "user_email": user_email,
        "indice_solvibilita": f"{punteggio_finale}/100",
        "esito_pratica": esito,
        "documento_ricevuto": nome_documento,
        "dettagli_analisi": motivi_penalizzazione if motivi_penalizzazione else ["Nessuna criticità rilevata."]
    }
