from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from datetime import date
from typing import Literal, Optional

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
        <title>Drive Scoring - Calcolo Solvibilità</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #2c3e50; }
            .container { background: white; max-width: 600px; margin: 30px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
            h1 { text-align: center; color: #2c3e50; margin-bottom: 10px; }
            p.subtitle { text-align: center; color: #7f8c8d; margin-bottom: 30px; }
            .form-group { margin-bottom: 20px; display: flex; flex-direction: column; }
            label { font-weight: 600; margin-bottom: 8px; font-size: 14px; }
            input[type="text"], input[type="number"], input[type="date"], input[type="email"], select { 
                padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 15px; width: 100%; box-sizing: border-box;
            }
            input[type="file"] { padding: 5px 0; }
            .optional-text { font-weight: normal; color: #7f8c8d; font-size: 12px; }
            .btn { background-color: #2ecc71; color: white; padding: 14px; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; transition: background 0.2s; }
            .btn:hover { background-color: #27ae60; }
            .footer { text-align: center; margin-top: 20px; font-size: 13px; }
            .footer a { color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Analisi Solvibilità Privati</h1>
            <p class="subtitle">Inserisci i dati richiesti per calcolare istantaneamente lo score finanziario.</p>
            
            <form action="/score/privato" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Email Utente</label>
                    <input type="email" name="user_email" required placeholder="esempio@email.com">
                </div>

                <div class="form-group">
                    <label>Tipologia Prodotto</label>
                    <select name="product_type" required>
                        <option value="finanziamento">Finanziamento</option>
                        <option value="leasing">Leasing</option>
                        <option value="NLT">NLT (Noleggio a Lungo Termine)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Durata Contratto (in mesi)</label>
                    <input type="number" name="contract_duration_months" required placeholder="Es. 36">
                </div>

                <div class="form-group">
                    <label>Rata Mensile Stimata (€)</label>
                    <input type="number" step="0.01" name="estimated_monthly_rate" required placeholder="Es. 250">
                </div>

                <div class="form-group">
                    <label>Anticipo Iniziale (€)</label>
                    <input type="number" step="0.01" name="initial_down_payment" required placeholder="Es. 1000">
                </div>

                <div class="form-group">
                    <label>Debiti/Rate Mensili Attuali (€)</label>
                    <input type="number" step="0.01" name="current_monthly_debts" required placeholder="Se nessuno metti 0">
                </div>

                <div class="form-group">
                    <label>Segnalazioni o Insolvenze Passate?</label>
                    <select name="has_credit_issues" required>
                        <option value="false">No (Nessun problema passato)</option>
                        <option value="true">Sì (Presenza di segnalazioni CRIF)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Data di Nascita</label>
                    <input type="date" name="birth_date" required>
                </div>

                <div class="form-group">
                    <label>Tipo di Contratto di Lavoro</label>
                    <select name="contract_type" required>
                        <option value="indeterminato">Tempo Indeterminato</option>
                        <option value="determinato">Tempo Determinato</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Settore Lavorativo Datore</label>
                    <input type="text" name="employer_sector" required placeholder="Es. Pubblico, Privato, Metalmeccanico">
                </div>

                <div class="form-group">
                    <label>Reddito Mensile Netto (€)</label>
                    <input type="number" step="0.01" name="net_monthly_income" required placeholder="Es. 1600">
                </div>

                <div class="form-group">
                    <label>Documento di Reddito <span class="optional-text">(Opzionale - Busta paga / CUD)</span></label>
                    <input type="file" name="documento_reddito" accept=".pdf, .png, .jpg, .jpeg">
                </div>

                <button type="submit" class="btn">Calcola Score Solvibilità</button>
            </form>
            
            <div class="footer">
                <a href="/docs">Accedi alla Documentazione API Tecnica</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/score/privato")
async def score_privato(
    request: Request,
    user_email: str = Form(...),
    product_type: Literal["finanziamento", "leasing", "NLT"] = Form(...),
    contract_duration_months: int = Form(...),
    estimated_monthly_rate: float = Form(...),
    initial_down_payment: float = Form(...),
    current_monthly_debts: float = Form(...),
    has_credit_issues: bool = Form(...),
    birth_date: date = Form(...),
    contract_type: Literal["indeterminato", "determinato"] = Form(...),
    employer_sector: str = Form(...),
    net_monthly_income: float = Form(...),
    documento_reddito: Optional[UploadFile] = File(None)
):
    nome_documento = "Non caricato"

    if documento_reddito and documento_reddito.filename:
        if not documento_reddito.filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            raise HTTPException(
                status_code=400, 
                detail="Formato file non valido. Caricare esclusivamente un file PDF o un'immagine (PNG, JPG)."
            )
        await documento_reddito.read()
        nome_documento = documento_reddito.filename

    # Algoritmo di Credit Scoring
    punteggio = 100
    motivi_penalizzazione = []
    
    if has_credit_issues:
        punteggio -= 40
        motivi_penalizzazione.append("Presenza di segnalazioni o insolvenze creditizie.")
        
    if contract_type == "determinato":
        punteggio -= 20
        motivi_penalizzazione.append("Contratto di lavoro a tempo determinato.")
        
    impegno_mensile_totale = estimated_monthly_rate + current_monthly_debts
    rapporto_indebitamento = impegno_mensile_totale / net_monthly_income if net_monthly_income > 0 else 1
    
    if rapporto_indebitamento > 0.35:
        punteggio -= 25
        motivi_penalizzazione.append("Rapporto rata/reddito troppo elevato (superiore al 35%).")

    oggi = date.today()
    eta_utente = oggi.year - birth_date.year - ((oggi.month, oggi.day) < (birth_date.month, birth_date.day))
    if eta_utente < 22 or eta_utente > 67:
        punteggio -= 10
        motivi_penalizzazione.append("Età fuori dalla fascia ottimale di finanziabilità.")

    punteggio_finale = max(0, punteggio)

    # Definizione esito e colori grafici
    if punteggio_finale >= 70:
        esito = "APPROVATO"
        colore_badge = "#2ecc71"
    elif punteggio_finale >= 45:
        esito = "DA VERIFICARE"
        colore_badge = "#e67e22"
    else:
        esito = "RIFIUTATO"
        colore_badge = "#e74c3c"

    # Se la richiesta arriva dal form del browser, restituiamo la pagina grafica
    accept_header = request.headers.get("accept", "")
    if "text/html" in accept_header:
        dettagli_html = "".join([f"<li>{motivo}</li>" for motivo in motivi_penalizzazione]) if motivi_penalizzazione else "<li>Nessuna criticità rilevata. Profilo finanziario ottimale.</li>"
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Report Solvibilità - Risultato</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
                .card {{ background: white; max-width: 550px; width: 100%; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.06); text-align: center; }}
                .badge {{ display: inline-block; padding: 10px 20px; color: white; background-color: {colore_badge}; border-radius: 50px; font-weight: bold; font-size: 18px; margin-bottom: 20px; letter-spacing: 1px; }}
                .score-text {{ font-size: 48px; font-weight: 800; color: #2c3e50; margin: 10px 0; }}
                .progress-container {{ background-color: #e0e0e0; border-radius: 8px; height: 12px; width: 100%; margin: 20px 0 30px 0; overflow: hidden; }}
                .progress-bar {{ background-color: {colore_badge}; height: 100%; width: {punteggio_finale}%; transition: width 0.5s ease-in-out; }}
                .details-box {{ text-align: left; background-color: #f8f9fa; border-left: 4px solid {colore_badge}; padding: 15px 20px; border-radius: 0 8px 8px 0; margin-bottom: 30px; }}
                .details-box h3 {{ margin-top: 0; color: #34495e; font-size: 16px; }}
                .details-box ul {{ padding-left: 20px; margin: 5px 0 0 0; color: #7f8c8d; font-size: 14px; line-height: 1.6; }}
                .btn-back {{ display: inline-block; background-color: #34495e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 15px; transition: background 0.2s; }}
                .btn-back:hover {{ background-color: #2c3e50; }}
                .info-meta {{ font-size: 13px; color: #95a5a6; margin-bottom: 25px; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">{esito}</div>
                <div class="score-text">{punteggio_finale}<span style="font-size: 20px; color: #95a5a6;">/100</span></div>
                
                <div class="progress-container">
                    <div class="progress-bar"></div>
                </div>

                <div class="details-box">
                    <h3>Dettagli Analisi del Rischio:</h3>
                    <ul>{dettagli_html}</ul>
                </div>

                <div class="info-meta">
                    Pratica associata a: <strong>{user_email}</strong><br>
                    Prodotto richiesto: {product_type.upper()} | Documento: {nome_documento}
                </div>

                <a href="/" class="btn-back">Esegui un nuovo calcolo</a>
            </div>
        </body>
        </html>
        """)

    # Altrimenti (da /docs o script esterni), restituisce il JSON classico
    return {
        "status": "success",
        "user_email": user_email,
        "product_type": product_type,
        "contract_type": contract_type,
        "indice_solvibilita": f"{punteggio_finale}/100",
        "esito_pratica": esito,
        "documento_ricevuto": nome_documento,
        "dettagli_analisi": motivi_penalizzazione if motivi_penalizzazione else ["Nessuna criticità rilevata."]
    }
