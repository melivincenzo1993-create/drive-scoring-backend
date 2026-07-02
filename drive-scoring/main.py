from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from datetime import date

app = FastAPI(
    title="Drive Scoring API",
    description="Backend per il calcolo dell'indice di solvibilità finanziaria.",
    version="1.0.0"
)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drive Scoring - Verifica Solvibilità</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background-color: #f4f7f6; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                min-height: 100vh; 
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
                text-align: center; 
                max-width: 500px; 
                width: 100%; 
            }
            h1 { 
                color: #2c3e50; 
                margin-bottom: 10px; 
            }
            p { 
                color: #7f8c8d; 
                font-size: 16px; 
                margin-bottom: 30px; 
                line-height: 1.5;
            }
            .btn { 
                display: inline-block; 
                background-color: #2ecc71; 
                color: white; 
                padding: 14px 28px; 
                text-decoration: none; 
                border-radius: 6px; 
                font-weight: bold; 
                font-size: 16px;
                transition: background 0.2s; 
                box-shadow: 0 4px 6px rgba(46, 204, 113, 0.2);
            }
            .btn:hover { 
                background-color: #27ae60; 
            }
            .footer-link { 
                margin-top: 25px; 
                display: block; 
                color: #95a5a6; 
                font-size: 13px; 
                text-decoration: none; 
            }
            .footer-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Analisi Solvibilità Privati</h1>
            <p>Benvenuto nella piattaforma di Credit Scoring di Drive Scoring. Valuta l'affidabilità creditizia in pochi istanti e invia i documenti per la verifica.</p>
            <a href="/docs" class="btn">Apri il Form di Test (Docs)</a>
            <a href="/docs" class="footer-link">Documentazione API v1.0.0</a>
        </div>
    </body>
    </html>
    """

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
    if not documento_reddito.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
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

    # Controllo età (es. prof profiles troppo giovani o in età pensionabile avanzata)
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
