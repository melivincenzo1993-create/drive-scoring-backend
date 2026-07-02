from weasyprint import HTML
import io
from datetime import date

def create_premium_pdf(first_name, last_name):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 20mm; }}
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #334155; line-height: 1.6; }}
            
            .header {{ border-bottom: 3px solid #0f172a; padding-bottom: 20px; margin-bottom: 40px; }}
            .brand {{ font-size: 24pt; font-weight: 800; color: #0f172a; letter-spacing: -1px; }}
            .meta {{ font-size: 9pt; color: #64748b; float: right; }}
            
            .status-box {{ background: #f1f5f9; padding: 20px; border-radius: 8px; border-left: 5px solid #dc2626; margin-bottom: 30px; }}
            .status-text {{ font-size: 10pt; font-weight: bold; color: #94a3b8; text-transform: uppercase; }}
            .status-value {{ font-size: 20pt; font-weight: 900; color: #dc2626; margin: 0; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            td {{ padding: 12px 0; border-bottom: 1px solid #e2e8f0; font-size: 11pt; }}
            .label {{ color: #64748b; width: 40%; }}
            .value {{ font-weight: 600; text-align: right; color: #0f172a; }}
            
            .footer {{ font-size: 8pt; color: #94a3b8; margin-top: 60px; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="brand">DRIVE SCORING</div>
            <div class="meta">REPORT DI VALUTAZIONE<br>Data: {date.today().strftime('%d/%m/%Y')}</div>
        </div>
        
        <div class="status-box">
            <div class="status-text">Esito Pratica</div>
            <div class="status-value">RIFIUTATO</div>
        </div>

        <table>
            <tr><td class="label">Richiedente</td><td class="value">{last_name.upper()} {first_name.upper()}</td></tr>
            <tr><td class="label">Punteggio Solvibilità</td><td class="value">40 / 100</td></tr>
        </table>

        <div class="footer">
            Documento generato automaticamente. Riservato.
        </div>
    </body>
    </html>
    """
    pdf_file = HTML(string=html_content).write_pdf()
    return io.BytesIO(pdf_file)
