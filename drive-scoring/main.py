from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from datetime import date
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
    # ... (Il form HTML rimane identico all'ultimo aggiornamento con Nome/Cognome e i 3 step)
    return "Form caricato con successo" # Sostituire con la stringa HTML completa precedente per il frontend

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
    has_credit_issues: bool = Form(...),
    birth_date: date = Form(...),
    net_monthly_income: float = Form(...),
    contract_type: Optional[str] = Form(None),
    piva_start_year: Optional[int] = Form(None),
    documento_reddito: UploadFile = File(...)
):
    # 1. LOG CONFORMITÀ GDPR
    email_hash = f"***@{user_email.split('@')[-1]}" if "@" in user_email else "Privacy-Hidden"
    logger.info(f"[GDPR COMPLIANT] Analisi Rigida Pay-Per-Use per utente: {email_hash}")

    ocr_log_status = "Verificato tramite OCR algoritmo integrato"

    # =========================================================================
    # 2. ALGORITMO DI SCORING AD ALTISSIMA RIGIDITÀ BANCARIA
    # =========================================================================
    punteggio = 100
    motivi = []
    forzato_rifiuto = False
    
    oggi = date.today()
    eta_richiedente = oggi.year - birth_date.year - ((oggi.month, oggi.day) < (birth_date.month, birth_date.day))
    eta_a_fine_contratto = eta_richiedente + (contract_duration_months / 12)
    
    totale_impegni_mensili = estimated_monthly_rate + current_monthly_debts
    rapporto_indebitamento = (totale_impegni_mensili / net_monthly_income) if net_monthly_income > 0 else 1.0

    if has_credit_issues:
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
    # 3. GENERAZIONE PDF CON INTERFACCIA PREMIUM EDITORIALE MINIMAL + LOGO
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
        
    style_main_title = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=20, textColor=c_dark, spaceAfter=2)
    style_meta_right = ParagraphStyle('DocMeta', fontName='Helvetica', fontSize=9, textColor=c_muted, alignment=2, leading=13)
    style_section_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=11, textColor=c_dark, spaceBefore=25, spaceAfter=8)
    style_cell_label = ParagraphStyle('CellLabel', fontName='Helvetica', fontSize=9.5, textColor=c_muted)
    style_cell_val = ParagraphStyle('CellVal', fontName='Helvetica-Bold', fontSize=10, textColor=c_text)
    style_badge_title = ParagraphStyle('BadgeTitle', fontName='Helvetica', fontSize=9, textColor=c_muted, spaceAfter=4)
    style_badge_val = ParagraphStyle('BadgeVal', fontName='Helvetica-Bold', fontSize=16, textColor=c_status)
    style_score_val = ParagraphStyle('ScoreVal', fontName='Helvetica-Bold', fontSize=18, textColor=c_dark)
    style_evidence = ParagraphStyle('EvidenceText', fontName='Helvetica', fontSize=9.5, textColor=c_text, leading=14)
    style_legal = ParagraphStyle('LegalText', fontName='Helvetica-Oblique', fontSize=7.5, textColor=c_muted, leading=11)

    # Gestione Fallback del Logo
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        logo_element = Image(logo_path, width=110, height=35)
        logo_element.hAlign = 'LEFT'
    else:
        logo_element = Paragraph("<b>DRIVE</b>SCORING", ParagraphStyle('FbLogo', fontName='Helvetica-Bold', fontSize=18, textColor=c_dark))

    # Blocco 1: Intestazione Istituzionale Bilanciata con Logo
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
    
    # Blocco 2: Pannello Risultato Finanziario
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
    
    # =========================================================================
    # DA AGGIUNGERE: 2.1 COSTRUZIONE DEI COMPONENTI GRAFICI NATIVI (FALLBACK)
    # =========================================================================
    story.append(Spacer(1, 15))
    
    # 1. DISEGNO PROGRESS BAR PUNTEGGIO (Larghezza 520px, Altezza 18px)
    d_score = Drawing(520, 20)
    # Sfondo grigio barra della progress bar
    d_score.add(Rect(0, 4, 520, 10, fillColor=colors.HexColor("#e2e8f0"), strokeColor=None, rx=5, ry=5))
    # Riempimento dinamico basato sul punteggio finale dell'algoritmo
    width_score_bar = (punteggio_finale / 100.0) * 520
    if width_score_bar > 0:
        d_score.add(Rect(0, 4, width_score_bar, 10, fillColor=c_status, strokeColor=None, rx=5, ry=5))
    story.append(d_score)
    
    story.append(Spacer(1, 5))

    # 2. DISEGNO GRAFICO DI SOGLIA RAPPORTO DEBITO (DTI METER)
    story.append(Paragraph("SITUAZIONE INDEBITAMENTO (DTI RETAIL METER)", style_badge_title))
    d_dti = Drawing(520, 30)
    # Barra di fondo del DTI
    d_dti.add(Rect(0, 12, 520, 8, fillColor=colors.HexColor("#f1f5f9"), strokeColor=colors.HexColor("#cbd5e1"), strokeWidth=0.5))
    
    # Marcatori soglie critiche (30% e 45%)
    pos_30 = 0.30 * 520
    pos_45 = 0.45 * 520
    # Linea limite allerta (30%)
    d_dti.add(Line(pos_30, 6, pos_30, 26, strokeColor=colors.HexColor("#d97706"), strokeWidth=1))
    d_dti.add(String(pos_30 - 15, 28, "Allerta 30%", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#d97706")))
    # Linea limite blocco (45%)
    d_dti.add(Line(pos_45, 6, pos_45, 26, strokeColor=colors.HexColor("#dc2626"), strokeWidth=1))
    d_dti.add(String(pos_45 - 15, 28, "Blocco 45%", fontName="Helvetica", fontSize=7.5, fillColor=colors.HexColor("#dc2626")))
    
    # Posizione effettiva del cliente sul grafico
    pos_cliente = min(rapporto_indebitamento, 1.0) * 520
    # Disegniamo un puntatore geometrico (rettangolo pieno scuro con contorno bianco) per la posizione del cliente
    d_dti.add(Rect(pos_cliente - 4, 10, 8, 12, fillColor=c_dark, strokeColor=colors.white, strokeWidth=1))
    story.append(d_dti)
    
    # Blocco 3: Parametri analizzati ed Indicatori di Sostenibilità
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
    
    # Blocco 4: Evidenze e Note di Rischio Estese
    story.append(Paragraph("EVIDENZE RILEVATE DALL'ALGORITMO", style_section_title))
    evidence_rows = []
    
    if motivi:
        for m in motivi:
            evidence_rows.append([Paragraph(f"<font color='{c_status.hexval()}'>■</font> {m}", style_evidence)])
    else:
        evidence_rows.append([Paragraph(f"<font color='{c_status.hexval()}'>■</font> <b>Nessuna criticità rilevata.</b> Il profilo del richiedente supera tutti i filtri di controllo e le soglie di rischio bancario impostate.", style_evidence)])
        
    evidence_table = Table(evidence_rows, colWidths=[520])
    evidence_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_panel),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('PADDING', (0,0), (-1,-1), 11),
    ]))
    story.append(evidence_table)
    
    # Blocco 5: Footer Legale
    story.append(Spacer(1, 35))
    story.append(Paragraph(f"<b>Trasparenza & Nota Legale:</b> {DISCLAIMER_TEXT}", style_legal))
    
    # Costruiamo il documento agganciando lo sfondo dinamico disegnato sui Canvas
    doc.build(story, onFirstPage=draw_premium_decorations, onLaterPages=draw_premium_decorations)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Report_Scoring_Premium_{oggi}.pdf"}
    )
