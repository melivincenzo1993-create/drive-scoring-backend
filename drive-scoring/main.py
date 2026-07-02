from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from weasyprint import HTML, CSS
import io
from datetime import date

app = FastAPI()

@app.post("/score/premium")
async def generate_pdf(
    first_name: str = Form(...),
    last_name: str = Form(...)
):
    # Dati simulati per l'esempio
    score = 40
    status = "RIFIUTATO"
    
    # Design CSS avanzato
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 20mm; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6; }}
            
            /* Header Style */
            .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0f172a; padding-bottom: 15px; margin-bottom: 30px; }}
            .brand {{ font-size: 26pt; font-weight: 800; color: #0f172a; letter-spacing: -1px; }}
            
            /* Card & Badge */
            .card-status {{ background: #fef2f2; border: 1px solid #fecaca; padding: 20px; border-radius: 12px; margin-bottom: 25px; }}
            .status-text {{ font-size: 22pt; font-weight: 800; color: #dc2626; }}
            
            /* Dati */
            .data-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .data-table td {{ padding: 15px; border-bottom: 1px solid #e2e8f0; }}
            .label {{ color: #64748b; font-size: 10pt; text-transform: uppercase; }}
            .value {{ font-weight: 700; text-align: right; }}
            
            .legal {{ font-size: 7.5pt; color: #94a3b8; margin-top: 60px; font-style: italic; border-top: 1px solid #f1f5f9; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="brand">DRIVE SCORING</div>
            <div style="text-align: right; color: #64748b;">Report di Pre-Delibera<br>{date.today().strftime('%d/%m/%Y')}</div>
        </div>
        
        <div class="card-status">
            <div style="font-size: 9pt; color: #991b1b; margin-bottom: 5px;">ESITO DELLA VERIFICA</div>
            <div class="status-text">{status}</div>
        </div>

        <table class="data-table">
            <tr><td class="label">Richiedente</td><td class="value">{last_name.upper()} {first_name.upper()}</td></tr>
            <tr><td class="label">Indice di Solvibilità</td><td class="value">{score}/100</td></tr>
        </table>
        
        <div class="legal">
            Nota Legale: Il presente documento è generato automaticamente per fini di pre-scoring. 
            Il risultato non costituisce un impegno contrattuale.
        </div>
    </body>
    </html>
    """

    pdf_bytes = HTML(string=html_template).write_pdf()
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=Report_Premium.pdf"}
    )
