from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import schemas
import engine
import models
import pdf_generator
from database import engine_db, get_db
from datetime import datetime

# Inizializza automaticamente le tabelle nel database SQLite se non esistono
models.Base.metadata.create_all(bind=engine_db)

app = FastAPI(
    title="Drive Scoring API",
    description="Motore di calcolo, persistenza dati su SQLite e generazione automatica di Report PDF.",
    version="1.5"
)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drive Scoring API</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    </head>
    <body class="bg-slate-900 text-slate-100 font-sans flex flex-col justify-between min-h-screen">
        
        <!-- Header -->
        <header class="p-6 max-w-6xl mx-auto w-full flex justify-between items-center">
            <div class="flex items-center gap-2 font-bold text-xl tracking-wide text-emerald-400">
                <span>🚗</span> Drive Scoring
            </div>
            <span class="px-3 py-1 text-xs font-semibold bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Operational
            </span>
        </header>

        <!-- Main Content -->
        <main class="max-w-4xl mx-auto px-6 text-center py-20 my-auto">
            <h1 class="text-5xl font-extrabold tracking-tight mb-4 bg-gradient-to-r from-emerald-400 to-teal-200 bg-clip-text text-transparent">
                Drive Scoring Backend
            </h1>
            <p class="text-lg text-slate-400 max-w-xl mx-auto mb-10">
                Il motore di analisi e calcolo dei punteggi di guida. Servizio API REST sicuro, veloce e scalabile, ottimizzato per il tuo frontend.
            </p>
            
            <div class="flex justify-center gap-4">
                <a href="/docs" class="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-medium rounded-lg transition-all shadow-lg shadow-emerald-500/10">
                    Esplora la Documentazione (Swagger)
                </a>
                <a href="/redoc" class="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-lg transition-all border border-slate-700">
                    ReDoc Alternative
                </a>
            </div>
        </main>

        <!-- Footer -->
        <footer class="p-6 text-center text-sm text-slate-500 border-t border-slate-800 max-w-6xl mx-auto w-full">
            &copy; 2026 Drive Scoring Project. Hosted with &hearts; on Render.
        </footer>

    </body>
    </html>
    """

# ==========================================
# 1. ENDPOINT PRIVATO
# ==========================================
@app.post("/score/privato")
def score_privato(dati: schemas.PrivatoRequest):
    # 1. Importiamo la funzione dal file engine
    from engine import calcola_score_privato
    
    # 2. Eseguiamo il calcolo matematico dello score finanziario
    risultato_scoring = calcola_score_privato(dati)
    
    # 3. Restituiamo direttamente la risposta al frontend senza toccare il database
    return risultato_scoring
