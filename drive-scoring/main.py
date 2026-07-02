from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from pdf_generator import create_premium_pdf
import uvicorn

app = FastAPI()

# 1. Landing Page integrata (appare alla home page)
@app.get("/")
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Drive Scoring | Portale Richiesta</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 100%; max-width: 350px; text-align: center; }
            h2 { margin-bottom: 20px; color: #f8fafc; }
            input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #dc2626; border: none; border-radius: 6px; color: white; font-weight: bold; cursor: pointer; margin-top: 10px; }
            button:hover { background: #b91c1c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Drive Scoring</h2>
            <p>Richiedi il tuo report</p>
            <form action="/score/premium" method="POST">
                <input type="text" name="first_name" placeholder="Nome" required>
                <input type="text" name="last_name" placeholder="Cognome" required>
                <button type="submit">Genera Report Premium</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 2. Endpoint per la generazione del PDF
@app.post("/score/premium")
async def generate_pdf(first_name: str = Form(...), last_name: str = Form(...)):
    # Chiama la funzione dal tuo file pdf_generator.py
    pdf_bytes = create_premium_pdf(first_name, last_name)
    
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Report_Premium.pdf"}
    )
