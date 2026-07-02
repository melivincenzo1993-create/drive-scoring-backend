from fastapi import FastAPI, UploadFile, File, Form, HTTPException

app = FastAPI()

@app.post("/calcola-indice-privato")
async def calcola_indice_privato(
    eta: int = Form(...),
    contratto_indeterminato: bool = Form(...),
    reddito_mensile: float = Form(...),
    finanziamenti_in_corso: bool = Form(...),
    segnalazioni_insolvenze: bool = Form(...),
    importo_richiesto: float = Form(...),
    documento_reddito: UploadFile = File(...)
):
    # 1. Verifica che sia stato caricato un file valido
    if not documento_reddito.filename.endswith(('.pdf', '.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Carica un documento valido (PDF o Immagine).")

    # Legge il file in memoria
    contenuto_file = await documento_reddito.read()
    nome_documento = documento_reddito.filename

    # 2. Logica del tuo algoritmo di calcolo della solvibilità
    punteggio = 100
    
    if eta < 25 or eta > 65: punteggio -= 10
    if not contratto_indeterminato: punteggio -= 25
    if finanziamenti_in_corso: punteggio -= 15
    if segnalazioni_insolvenze: punteggio -= 40
    
    rapporto_rata = (importo_richiesto / 12) / reddito_mensile
    if rapporto_rata > 0.35: punteggio -= 20

    if punteggio >= 70:
        esito = "Approvato"
    elif punteggio >= 50:
        esito = "Da verificare"
    else:
        esito = "Rifiutato"

    # 3. Risposta inviata allo schermo
    return {
        "status": "success",
        "indice_solvibilita": max(0, punteggio),
        "esito_pratica": esito,
        "documento_elaborato": nome_documento
    }
