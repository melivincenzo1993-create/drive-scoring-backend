from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from weasyprint import HTML
import io
from datetime import date

app = FastAPI()

@app.post("/score/premium")
async def generate_pdf(
    first_name: str = Form(...),
    last_name: str = Form(...),
    # ... (tutti gli altri campi)
):
    # 1. Logica di calcolo (es. punteggio = 40)
    # ...
    
    # 2. Design HTML/CSS Moderno
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 20mm; }}
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; }}
            .header {{ border-bottom: 2px solid #0f172a; padding-bottom: 10px; margin-bottom: 20px; }}
            .brand {{ font-size: 24pt; font-weight: bold; color: #0f172a; }}
            .card {{ border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; background: #f8fafc; }}
            .status-badge {{ font-size: 18pt; font-weight: bold; color: #dc2626; }}
            .metric {{ font-size: 28pt; font-weight: bold; }}
            .table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .table td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
            .label {{ color: #64748b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="brand">DRIVE SCORING</div>
            <div style="text-align: right;">Report di Pre-Delibera | {date.today().strftime('%d/%m/%Y')}</div>
        </div>
        
        <div class="card">
            <div class="status-badge">RIFIUTATO</div>
            <div style="font-size: 10pt; color: #64748b;">ESITO ANALISI</div>
        </div>

        <table class="table">
            <tr><td class="label">Richiedente</td><td style="text-align:right;">{last_name.upper()} {first_name.upper()}</td></tr>
            <tr><td class="label">Indice Solvibilità</td><td style="text-align:right;"><b>40/100</b></td></tr>
        </table>
        
        <p style="font-size: 8pt; color: #94a3b8; margin-top: 50px;">
            Nota Legale: Risultato indicativo ai sensi delle direttive bancarie.
        </p>
    </body>
    </html>
    """

    # 3. Generazione PDF
    pdf_bytes = HTML(string=html_template).write_pdf()
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Report_Premium.pdf"}
    )
