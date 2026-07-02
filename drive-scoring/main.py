from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from weasyprint import HTML
import io
from datetime import date

app = FastAPI()

@app.post("/score/premium")
async def generate_pdf(first_name: str = Form(...), last_name: str = Form(...)):
    
    # Template HTML con CSS incorporato per un design professionale
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 25mm; }}
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.5; }}
            .header {{ display: table; width: 100%; border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 30px; }}
            .brand {{ display: table-cell; font-size: 26pt; font-weight: 800; color: #0f172a; letter-spacing: -1px; }}
            .meta {{ display: table-cell; text-align: right; font-size: 9pt; color: #64748b; }}
            .status-card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 30px; }}
            .status-label {{ font-size: 8pt; font-weight: 700; color: #94a3b8; text-transform: uppercase; }}
            .status-value {{ font-size: 24pt; font-weight: 800; color: #dc2626; margin-top: 5px; }}
            .data-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            .data-table td {{ padding: 14px; border-bottom: 1px solid #f1f5f9; font-size: 10pt; }}
            .row-label {{ color: #64748b; }}
            .row-value {{ font-weight: 600; text-align: right; color: #0f172a; }}
            .legal {{ font-size: 7pt; color: #94a3b8; margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 10px; font-style: italic; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="brand">DRIVE SCORING</div>
            <div class="meta">REPORT DI PRE-DELIBERA<br>{date.today().strftime('%d/%m/%Y')}</div>
        </div>
        <div class="status-card">
            <div class="status-label">Esito valutazione</div>
            <div class="status-value">RIFIUTATO</div>
        </div>
        <table class="data-table">
            <tr><td class="row-label">Richiedente</td><td class="row-value">{last_name.upper()} {first_name.upper()}</td></tr>
            <tr><td class="row-label">Indice Solvibilità</td><td class="row-value">40 / 100</td></tr>
        </table>
        <div class="legal">
            Nota di Trasparenza: Il documento è generato automaticamente. Questo strumento funge 
            esclusivamente da pre-scoring indicativo secondo parametri di sostenibilità bancaria.
        </div>
    </body>
    </html>
    """

    # Generazione PDF
    pdf_bytes = HTML(string=html_template).write_pdf()
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Report_Premium.pdf"}
    )
