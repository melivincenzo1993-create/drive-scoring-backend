import os
from xhtml2pdf import pisa

def genera_pdf_report(report_id: str, dati_report: dict, sub_scores: dict) -> str:
    output_dir = "reports_pdf"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf_filename = f"{output_dir}/Report_{report_id}.pdf"
    
    classi_config = {
        "A": {"colore": "#2e7d32", "sfondo": "#e8f5e9", "desc": "Eccellente - Profilo ad altissima affidabilità lavorativa e finanziaria."},
        "B": {"colore": "#1565c0", "sfondo": "#e3f2fd", "desc": "Buono - Profilo solido con parametri pienamente nella norma."},
        "C": {"colore": "#ef6c00", "sfondo": "#fff3e0", "desc": "Sotto la media - Richiede attenzione o garanzie integrative."},
        "D": {"colore": "#c62828", "sfondo": "#ffebee", "desc": "Rischio Elevato - Presenza di anomalie bloccanti o scarsa sostenibilità."}
    }
    
    cfg = classi_config.get(dati_report['risk_class'], classi_config["D"])
    ko_html = f'<div style="background-color: #ffebee; border-left: 4px solid #c62828; color: #c62828; padding: 12px; margin-bottom: 25px;"><strong>ATTENZIONE - ESITO NEGATIVO:</strong><br>{dati_report["ko_reason"]}</div>' if dati_report.get('ko_reason') else ''

    html_content = f'''
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: a4; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333333; font-size: 10pt; }}
            .header {{ border-bottom: 2px solid #1a365d; padding-bottom: 10px; margin-bottom: 25px; }}
            .logo-text {{ font-size: 24pt; font-weight: bold; color: #1a365d; }}
            .score-container {{ background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; margin-bottom: 25px; text-align: center; }}
            .score-badge {{ font-size: 42pt; font-weight: bold; color: {cfg['colore']}; }}
            .class-badge {{ padding: 5px 15px; font-size: 12pt; font-weight: bold; color: {cfg['colore']}; background-color: {cfg['sfondo']}; }}
            table {{ width: 100%; margin-bottom: 20px; }}
            th {{ background-color: #f7fafc; padding: 8px; text-align: left; font-weight: bold; }}
            td {{ padding: 8px; border-bottom: 1px solid #edf2f7; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-text">DRIVE SCORING</div>
            <div style="color: #555555;">Analisi Pre-Analitica Automotive</div>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <h2>CERTIFICATO DI PRE-QUALIFICAZIONE</h2>
            <div style="font-size: 9pt; color: #666666;">ID Report: {report_id} | Elaborato il: {dati_report['created_at']}</div>
        </div>
        <div class="score-container">
            <div class="score-badge">{dati_report['final_score']}/100</div><br>
            <span class="class-badge">CLASSE {dati_report['risk_class']}</span>
            <p style="color: #4a5568;">{cfg['desc']}</p>
        </div>
        {ko_html}
        <h3>Dati della Richiesta</h3>
        <table>
            <tr><th>Parametro</th><th>Valore</th></tr>
            <tr><td><strong>Email Utente:</strong></td><td>{dati_report['user_email']}</td></tr>
            <tr><td><strong>Tipo Prodotto:</strong></td><td>{dati_report['product_type']}</td></tr>
            <tr><td><strong>Profilo Selezionato:</strong></td><td>{dati_report['target_profile']}</td></tr>
            <tr><td><strong>Durata Contratto:</strong></td><td>{dati_report['contract_duration_months']} mesi</td></tr>
            <tr><td><strong>Rata Mensile Stimata:</strong></td><td>€ {dati_report['estimated_monthly_rate']}</td></tr>
        </table>
        <h3>Punteggi parziali</h3>
        <p>Sostenibilità: {sub_scores.get('sostenibilita', 0)}/100</p>
        <p>Stabilità Lavorativa: {sub_scores.get('stabilita', 0)}/100</p>
        <p>Anagrafica: {sub_scores.get('anagrafica', 0)}/100</p>
        <p>Storico Creditizio: {sub_scores.get('storico', 0)}/100</p>
    </body>
    </html>
    '''
    
    with open(pdf_filename, "w+b") as result_file:
        pisa.CreatePDF(html_content, dest=result_file)
        
    return pdf_filename
    