from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from datetime import datetime, date
from typing import Literal, Optional
import io
import math
import logging
import os

# Import per la generazione del PDF ad Alto Impatto Grafico
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Import per i componenti Grafici Nativi del PDF (Fallback Grafico)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

# Configurazione Log di Sicurezza (GDPR Compliant)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DriveScoringPremium")

app = FastAPI(
    title="Drive Scoring API - Premium Edition",
    version="2.0.0"
)

DISCLAIMER_TEXT = (
    "ATTENZIONE: Il risultato ottenuto ha un valore puramente indicativo e non garantisce in alcun modo "
    "l'approvazione del finanziamento o del contratto. Questo strumento funge esclusivamente da pre-scoring "
    "per valutare preliminarmente il profilo finanziario del richiedente secondo rigidi parametri di sostenibilità bancaria."
)

# Funzione per disegnare lo sfondo premium della pagina (Canvas Layer)
def draw_premium_decorations(canvas, doc):
    canvas.saveState()
    # Barra superiore color Slate scuro elegante
    canvas.setFillColor(colors.HexColor("#0f172a"))
    canvas.rect(0, 770, 612, 22, fill=True, stroke=False)
    
    # Linea decorativa sottile sul margine sinistro
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(35, 40, 35, 740)
    canvas.restoreState()

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drive Scoring Premium — Analisi Guidata</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #f1f5f9;
                --card-bg: #ffffff;
                --text-main: #0f172a;
                --text-muted: #64748b;
                --border-color: #e2e8f0;
                --primary: #10b981;
                --primary-hover: #059669;
                --accent-warn: #fef3c7;
                --text-warn: #d97706;
                --border-warn: #fde68a;
            }}
            
            body {{ 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                margin: 0; 
                padding: 60px 20px; 
                color: var(--text-main);
                -webkit-font-smoothing: antialiased;
                min-height: 100vh;
                box-sizing: border-box;
            }}
            
            .container {{ 
                background: var(--card-bg); 
                max-width: 580px; 
                margin: 0 auto; 
                padding: 45px; 
                border-radius: 24px; 
                box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.06), 0 1px 3px rgba(0,0,0,0.02);
                border: 1px solid rgba(226, 232, 240, 0.8);
            }}
            
            h1 {{ 
                text-align: center; 
                font-size: 28px; 
                font-weight: 700; 
                letter-spacing: -0.03em; 
                margin-bottom: 6px; 
                color: #0f172a;
            }}
            p.subtitle {{ 
                text-align: center; 
                color: var(--text-muted); 
                font-size: 15px; 
                margin-top: 0; 
                margin-bottom: 40px; 
            }}
            
            /* Step Progress Bar */
            .steps-indicator {{ 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 40px; 
                position: relative; 
                max-width: 400px;
                margin-left: auto;
                margin-right: auto;
            }}
            .steps-indicator::before {{ 
                content: ''; 
                position: absolute; 
                top: 16px; 
                left: 0; 
                right: 0; 
                height: 2px; 
                background: #e2e8f0; 
                z-index: 1; 
            }}
            .step-dot {{ 
                width: 34px; 
                height: 34px; 
                border-radius: 50%; 
                background: #fff; 
                border: 2px solid #e2e8f0; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 14px; 
                font-weight: 600; 
                color: var(--text-muted); 
                z-index: 2; 
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
            }}
            .step-dot.active {{ 
                border-color: var(--primary); 
                background: var(--primary); 
                color: #fff; 
                box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
            }}
            .step-dot.completed {{ 
                border-color: var(--primary); 
                background: #ecfdf5; 
                color: var(--primary); 
            }}

            /* Form Step Animations */
            .form-step {{ 
                display: none; 
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease-in-out;
            }}
            .form-step.active {{ 
                display: block; 
                opacity: 1;
                transform: translateY(0);
            }}
            
            .form-group {{ margin-bottom: 24px; display: flex; flex-direction: column; }}
            label {{ font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #1e293b; }}
            
            input[type="text"], input[type="number"], input[type="date"], input[type="email"], select {{ 
                padding: 14px 16px; 
                border: 1px solid var(--border-color); 
                border-radius: 12px; 
                font-size: 15px; 
                width: 100%; 
                box-sizing: border-box; 
                transition: all 0.2s ease;
                background-color: #f8fafc;
            }}
            input:focus, select:focus {{ 
                outline: none; 
                border-color: var(--primary); 
                background-color: #fff;
                box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1); 
            }}
            
            .btn-container {{ display: flex; justify-content: space-between; margin-top: 35px; gap: 16px; }}
            .btn {{ 
                background-color: var(--primary); 
                color: white; 
                padding: 16px; 
                border: none; 
                border-radius: 12px; 
                font-weight: 600; 
                font-size: 16px; 
                cursor: pointer; 
                flex: 1; 
                transition: all 0.2s ease; 
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
            }}
            .btn:hover {{ 
                background-color: var(--primary-hover); 
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(16, 185, 129, 0.15);
            }}
            
            .btn-secondary {{ 
                background-color: #fff; 
                color: #475569; 
                border: 1px solid var(--border-color); 
            }}
            .btn-secondary:hover {{ 
                background-color: #f8fafc; 
            }}
            
            .gdpr-box {{ 
                display: flex; 
                align-items: flex-start; 
                gap: 12px; 
                margin-top: 20px; 
                font-size: 13px; 
                color: var(--text-muted); 
            }}
            .gdpr-box input {{ margin-top: 3px; width: 16px; height: 16px; }}
            
            .value-propositions {{
                margin-top: 40px;
                padding-top: 30px;
                border-top: 1px solid var(--border-color);
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }}
            .prop-item {{
                font-size: 13px;
                color: var(--text-muted);
                display: flex;
                align-items: center;
                gap: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Drive Scoring Premium</h1>
            <p class="subtitle">Verifica affidabilità istantanea (Tariffa: 1 Credit / Pay-per-use)</p>
            
            <div class="steps-indicator">
                <div class="step-dot active" id="dot-1">1</div>
                <div class="step-dot" id="dot-2">2</div>
                <div class="step-dot" id="dot-3">3</div>
            </div>

            <form action="/score/premium" method="POST" enctype="multipart/form-data" id="scoring-form">
                
                <div class="form-step active" id="step-1">
                    <div style="display: flex; gap: 16px; margin-bottom: 0;">
                        <div class="form-group" style="flex: 1;">
                            <label>Nome</label>
                            <input type="text" name="first_name" required placeholder="Es. Mario">
                        </div>
                        <div class="form-group" style="flex: 1;">
                            <label>Cognome</label>
                            <input type="text" name="last_name" required placeholder="Es. Rossi">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Profilo Richiedente</label>
                        <select name="target_profile" id="target_profile" onchange="adjustProfileFields()" required>
                            <option value="privato_dipendente">Privato (Dipendente)</option>
                            <option value="libero_professionista">Libero professionista / Ditta individuale</option>
                            <option value="pensionato">Pensionato</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Email per invio Report</label>
                        <input type="email" name="user_email" required placeholder="cliente@email.com">
                    </div>
                    <div class="form-group">
                        <label>Data di Nascita</label>
                        <input type="date" name="birth_date" required>
                    </div>
                    <div class="btn-container">
                        <button type="button" class="btn" onclick="nextStep(2)">Avanti</button>
                    </div>
                </div>

                <div class="form-step" id="step-2">
                    <div class="form-group">
                        <label>Reddito Mensile Netto Medio (€)</label>
                        <input type="number" step="0.01" name="net_monthly_income" required placeholder="Es. 2200">
                    </div>
                    <div class="form-group">
                        <label>Carica Documento di Reddito (Scansione OCR)</label>
                        <input type="file" name="documento_reddito" accept=".pdf, .png, .jpg, .jpeg" required style="padding: 8px 0;">
                    </div>
                    
                    <div id="wrapper-piva" style="display:none;" class="form-group">
                        <label>Anno Apertura Partita IVA</label>
                        <input type="number" name="piva_start_year" placeholder="Es. 2018">
                    </div>
                    <div id="wrapper-dipendente" class="form-group">
                        <label>Tipo Contratto</label>
                        <select name="contract_type">
                            <option value="indeterminato">Tempo Indeterminato</option>
                            <option value="determinato">Tempo Determinato</option>
                        </select>
                    </div>

                    <div class="btn-container">
                        <button type="button" class="btn btn-secondary" onclick="prevStep(1)">Indietro</button>
                        <button type="button" class="btn" onclick="nextStep(3)">Avanti</button>
                    </div>
                </div>

                <div class="form-step" id="step-3">
                    <div class="form-group">
                        <label>Tipologia Prodotto</label>
                        <select name="product_type" required>
                            <option value="finanziamento">Finanziamento</option>
                            <option value="leasing">Leasing</option>
                            <option value="NLT">NLT (Noleggio a Lungo Termine)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Rata Mensile Stimata (€)</label>
                        <input type="number" step="0.01" name="estimated_monthly_rate" required placeholder="Es. 350">
                    </div>
                    <div class="form-group">
                        <label>Durata Contratto (Mesi)</label>
                        <input type="number" name="contract_duration_months" required placeholder="Es. 48">
                    </div>
                    <div class="form-group">
                        <label>Impegni/Rate mensili già attive (€)</label>
                        <input type="number" step="0.01" name="current_monthly_debts" value="0">
                    </div>
                    <div class="form-group">
                        <label>Segnalazioni pregiudizievoli (CRIF)</label>
                        <select name="has_credit_issues" required>
                            <option value="false">Nessuna segnalazione</option>
                            <option value="true">Sì, presenti segnalazioni</option>
                        </select>
                    </div>

                    <div class="gdpr-box">
                        <input type="checkbox" id="gdpr" required>
                        <label for="gdpr">Acconsento al trattamento dei dati secondo la normativa GDPR.</label>
                    </div>

                    <div class="btn-container">
                        <button type="button" class="btn btn-secondary" onclick="prevStep(2)">Indietro</button>
                        <button type="submit" class="btn" style="background-color: #0f172a;">Paga ed Elabora PDF</button>
                    </div>
                </div>
            </form>

            <div class="value-propositions">
                <div class="prop-item">✦ <strong>Report PDF</strong> incluso</div>
                <div class="prop-item">✦ Verifica <strong>OCR</strong></div>
                <div class="prop-item">✦ Crittografia <strong>GDPR</strong></div>
                <div class="prop-item">✦ Esito <strong>Istantaneo</strong></div>
            </div>
        </div>

        <script>
            function nextStep(step) {{
                if(step === 2) {{
                    document.getElementById('step-1').classList.remove('active');
                    setTimeout(() => {{
                        document.getElementById('step-2').classList.add('active');
                        document.getElementById('dot-1').classList.add('completed');
                        document.getElementById('dot-2').classList.add('active');
                    }}, 50);
                }}
                if(step === 3) {{
                    document.getElementById('step-2').classList.remove('active');
                    setTimeout(() => {{
                        document.getElementById('step-3').classList.add('active');
                        document.getElementById('dot-2').classList.add('completed');
                        document.getElementById('dot-3').classList.add('active');
                    }}, 50);
                }}
            }}
            function prevStep(step) {{
                if(step === 1) {{
                    document.getElementById('step-2').classList.remove('active');
                    setTimeout(() => {{
                        document.getElementById('step-1').classList.add('active');
                        document.getElementById('dot-2').classList.remove('active');
                        document.getElementById('dot-1').classList.remove('completed');
                    }}, 50);
                }}
                if(step === 2) {{
                    document.getElementById('step-3').classList.remove('active');
                    setTimeout(() => {{
                        document.getElementById('step-2').classList.add('active');
                        document.getElementById('dot-3').classList.remove('active');
                        document.getElementById('dot-2').classList.remove('completed');
                    }}, 50);
                }}
            }}
            function adjustProfileFields() {{
                var prof = document.getElementById('target_profile').value;
                document.getElementById('wrapper-piva').style.display = (prof === 'libero_professionista') ? 'block' : 'none';
                document.getElementById('wrapper-dipendente').style.display = (prof === 'privato_dipendente') ? 'block' : 'none';
            }}
        </script>
    </body>
    </html>
    """

@app.post("/score/premium")
async def score_premium(
    first_name: str = Form(...),
    last_name: str = Form(...),
    user_email: str = Form(...),
    target_profile: str = Form(...),
    product_type: str = Form(...),
    contract_duration_months: int = Form(...),
    estimated_monthly_rate: float = Form(...),
    current_monthly_debts: float = Form(...),
    has_credit_issues: str = Form(...),       # Ricevuto come stringa dal form multipart
    birth_date: str = Form(...),              # Ricevuto come stringa dal form multipart
    net_monthly_income: float = Form(...),
    contract_type: Optional[str] = Form(None),
    piva_start_year: Optional[int] = Form(None),
    documento_reddito: UploadFile = File(...)
):
    # Safe type parsing per impedire i crash di FastAPI
    is_credit_compromised = (has_credit_issues.lower() == "true")
    
    try:
        parsed_birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato Data di Nascita non valido. Usa AAAA-MM-GG.")

    email_hash = f"***@{user_email.split('@')[-1]}" if "@" in user_email else "Privacy-Hidden"
    logger.info(f"[GDPR] Analisi per utente: {email_hash}")

    # =========================================================================
    # ALGORITMO DI SCORING
    # =========================================================================
    punteggio = 100
    motivi = []
    forzato_rifiuto = False
    
    oggi = date.today()
    eta_richiedente = oggi.year - parsed_birth_date.year - ((oggi.month, oggi.day) < (parsed_birth_date.month, parsed_birth_date.day))
    eta_a_fine_contratto = eta_richiedente + (contract_duration_months / 12)
    
    totale_impegni_mensili = estimated_monthly_rate + current_monthly_debts
    rapporto_indebitamento = (totale_impegni_mensili / net_monthly_income) if net_monthly_income > 0 else 1.0

    if is_credit_compromised:
        punteggio = 0
        forzato_rifiuto = True
        motivi.append("Presenza di segnalazioni pregiudizievoli o negatività in Banche Dati (CRIF).")

    if rapporto_indebitamento > 0.45:
        punteggio = max(0, punteggio - 60)
        forzato_rifiuto = True
        motivi.append(f"Soglia critica DTI superata: l'impegno mensile complessivo ({rapporto_indebitamento*100:.1f}%) supera il limite massimo del 45%.")
    elif rapporto_indebitamento > 0.30:
        punteggio -= 25
        motivi.append(f"Rapporto Rata/Reddito elevato ({rapporto_indebitamento*100:.1f}%). Supera la soglia di allerta del 30%.")

    if net_monthly_income < 1400.0:
        punteggio -= 20
        motivi.append(f"Reddito netto inserito ({net_monthly_income:.2f} €) inferiore alla soglia minima prudenziale di sussistenza (1.400 €).")

    if target_profile == "libero_professionista" and piva_start_year:
        anzianita_piva = oggi.year - piva_start_year
        if anzianita_piva < 3:
            punteggio -= 30
            motivi.append(f"Anzianità Partita IVA insufficiente ({anzianita_piva} anni). Richiesto un minimo di 3 anni di attività continuativa.")
    elif target_profile == "privato_dipendente" and contract_type == "determinato":
        punteggio -= 25
        motivi.append("Contratto a tempo determinato. Mancanza di garanzia di continuità reddituale a lungo termine.")

    if eta_a_fine_contratto > 75:
        punteggio -= 20
        motivi.append(f"Età anagrafica stimata a scadenza contratto ({eta_a_fine_contratto:.1f} anni) superiore al limite massimo istituzionale di 75 anni.")

    punteggio_finale = max(0, min(100, punteggio))
    
    if forzato_rifiuto or punteggio_finale < 45:
        esito = "RIFIUTATO"
    elif punteggio_finale >= 80:
        esito = "APPROVATO"
    else:
        esito = "DA VERIFICARE"

    # =========================================================================
    # GENERAZIONE PDF
    # =========================================================================
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=45, 
        leftMargin=45, topMargin=45, bottomMargin=45
    )
    story = []
    
    c_dark = colors.HexColor("#0f172a")       
    c_text = colors.HexColor("#334155")       
    c_muted = colors.HexColor("#64748b")      
    c_border = colors.HexColor("#e2e8f0")     
    c_bg_panel = colors.HexColor("#f8fafc")   
    
    if esito == "APPROVATO":
        c_status = colors.HexColor("#059669")     
        c_status_bg = colors.HexColor("#f0fdf4")  
    elif esito == "DA VERIFICARE":
        c_status = colors.HexColor("#d97706")     
        c_status_bg = colors.HexColor("#fef9c3")  
    else:
        c_status = colors.HexColor("#dc2626")     
        c_status_bg = colors.HexColor("#fef2f2")  
        
    styles = getSampleStyleSheet()
    style_meta_right = ParagraphStyle('DocMeta', fontName='Helvetica', fontSize=9, textColor=c_muted, alignment=2, leading=13)
    style_section_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=11, textColor=c_dark, spaceBefore=25, spaceAfter=8)
    style_cell_label = ParagraphStyle('CellLabel', fontName='Helvetica', fontSize=9.5, textColor=c_muted)
    style_cell_val = ParagraphStyle('CellVal', fontName='Helvetica-Bold', fontSize=10, textColor=c_text)
    style_badge_title = ParagraphStyle('BadgeTitle', fontName='Helvetica', fontSize=9, textColor=c_muted, spaceAfter=4)
    style_badge_val = ParagraphStyle('BadgeVal', fontName='Helvetica-Bold', fontSize=16, textColor=c_status)
    style_score_val = ParagraphStyle('ScoreVal', fontName='Helvetica-Bold', fontSize=18, textColor=c_dark)
    style_evidence = ParagraphStyle('EvidenceText', fontName='Helvetica', fontSize=9.5, textColor=c_text, leading=14)
    style_legal = ParagraphStyle('LegalText', fontName='Helvetica-Oblique', fontSize=7.5, textColor=c_muted, leading=11)

    logo_path = "logo.png"
    if os.path.exists(logo_path):
        logo_element = Image(logo_path, width=110, height=35)
        logo_element.hAlign = 'LEFT'
    else:
        logo_element = Paragraph("<b>DRIVE</b>SCORING", ParagraphStyle('FbLogo', fontName='Helvetica-Bold', fontSize=18, textColor=c_dark))

    header_data = [
        [
            logo_element,
            Paragraph(f"<b>RIGIDO REPORT DI PRE-DELIBERA</b><br/>ID Pratica: DS-{math.prod([oggi.day, oggi.month])}<br/>Data Valutazione: {oggi.strftime('%d/%m/%Y')}", style_meta_right)
        ]
    ]
    header_table = Table(header_data, colWidths=[200, 320])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, c_dark), 
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    badge_data = [
        [
            [Paragraph("ESITO CRITERIO RESTRETTO", style_badge_title), Paragraph(esito, style_badge_val)],
            [Paragraph("INDICE SOLVIBILITÀ BANCARIO", style_badge_title), Paragraph(f"{punteggio_finale} <font size=10 color='{c_muted.hexval()}'>/ 100</font>", style_score_val)]
        ]
    ]
    badge_table = Table(badge_data, colWidths=[255, 255])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), c_status_bg), 
        ('BACKGROUND', (1,0), (1,0), c_bg_panel),  
        ('BOX', (0,0), (0,0), 0.5, c_border),
        ('BOX', (1,0), (1,0), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 14),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 15))
    
    # 1. PROGRESS BAR PUNTEGGI
    d_score = Drawing(520, 20)
    d_score.add(Rect(0, 4, 520, 10, fillColor=colors.HexColor("#e2e8f0"), strokeColor=None, rx=5, ry=5))
    width_score_bar = (punteggio_finale / 100.0) * 520
    if width_score_bar > 0:
        d_score.add(Rect(0, 4, width_score_bar, 10, fillColor=c_status, strokeColor=None, rx=5, ry=5))
    story.append(d_score)
    story.append(Spacer(1, 5))

    # 2. DTI GRAPHIC METER
    story.append(Paragraph("SITUAZIONE INDEBITAMENTO (DTI RETAIL METER)", style_badge_title))
    d_dti = Drawing(520, 30)
    d_dti.add(Rect(0, 12, 520, 8, fillColor=colors.HexColor("#f1f5f9"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=0.5))
    
    pos_30 = 0.30 * 520
    pos_45 = 0.45 * 520
    d_dti.add(Line(pos_30, 6, pos_30, 26, strokeColor=colors.HexColor("#d97706"), strokeWidth=1))
    d_dti.add(String(pos_30 - 15, 28, "Allerta 30%", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#d97706")))
    d_dti.add(Line(pos_45, 6, pos_45, 26, strokeColor=colors.HexColor("#dc2626"), strokeWidth=1))
    d_dti.add(String(pos_45 - 15, 28, "Blocco 45%", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#dc2626")))
    
    pos_cliente = min(rapporto_indebitamento, 1.0) * 520
    d_dti.add(Rect(pos_cliente - 4, 10, 8, 12, fillColor=c_dark, strokeColor=colors.white, strokeWidth=1))
    story.append(d_dti)
    
    story.append(Paragraph("METRICHE RESTRITTIVE DI AFFIDABILITÀ", style_section_title))
    
    tech_data = [
        [Paragraph("Richiedente (Nome e Cognome)", style_cell_label), Paragraph(f"{last_name.upper()} {first_name.upper()}", style_cell_val)],
        [Paragraph("Inquadramento Professionale", style_cell_label), Paragraph(target_profile.replace('_',' ').upper(), style_cell_val)],
        [Paragraph("Rapporto Rata/Reddito Corrente (DTI)", style_cell_label), Paragraph(f"{rapporto_indebitamento * 100:.1f}%", style_cell_val)],
        [Paragraph("Reddito Netto Mensile Analizzato", style_cell_label), Paragraph(f"{net_monthly_income:,.2f} €".replace(",", "."), style_cell_val)],
        [Paragraph("Incrocio OCR & Indicatori Antifrode", style_cell_label), Paragraph(ocr_log_status.upper(), style_cell_val)]
    ]
    tech_table = Table(tech_data, colWidths=[240, 280])
    tech_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 9),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, c_border), 
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), c_bg_panel),
        ('BACKGROUND', (0,2), (-1,2), c_bg_panel),
        ('BACKGROUND', (0,4), (-1,4), c_bg_panel),
    ]))
    story.append(tech_table)
    
    story.append(Paragraph("EVIDENZE RILEVATE DALL'ALGORITMO", style_section_title))
    evidence_rows = []
    
    if motivi:
        for m in motivi:
            evidence_rows.append([Paragraph(f"<font color='{c_status.hexval()}'>■</font> {m}", style_evidence)])
    else:
        evidence_rows.append([Paragraph(f"<font color='{c_status.hexval()}'>■</font> <b>Nessuna criticità rilevata.</b> Il profilo supera i filtri di controllo.", style_evidence)])
        
    evidence_table = Table(evidence_rows, colWidths=[520])
    evidence_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_panel),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 11),
    ]))
    story.append(evidence_table)
    
    story.append(Spacer(1, 35))
    story.append(Paragraph(f"<b>Trasparenza & Nota Legale:</b> {DISCLAIMER_TEXT}", style_legal))
    
    doc.build(story, onFirstPage=draw_premium_decorations, onLaterPages=draw_premium_decorations)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Report_Scoring_Premium_{oggi}.pdf"}
    )
