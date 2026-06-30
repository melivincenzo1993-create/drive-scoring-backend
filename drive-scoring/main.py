from fastapi import FastAPI, Depends, HTTPException
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

@app.get("/")
def home():
    return {
        "status": "online",
        "message": "Benvenuto nel motore di calcolo di Drive Scoring!"
    }

# ==========================================
# 1. ENDPOINT PRIVATO
# ==========================================
@app.post("/score/privato")
def score_privato(dati: schemas.PrivatoRequest, db: Session = Depends(get_db)):
    payload = dati.model_dump()
    
    # Calcolo del punteggio tramite il motore algoritmico
    risultato = engine.calcola_scoring(payload)
    
    # Salvataggio record principale (scoring_reports)
    nuovo_report = models.ScoringReport(
        user_email=dati.user_email,
        target_profile=dati.target_profile,
        product_type=dati.product_type,
        contract_duration_months=dati.contract_duration_months,
        estimated_monthly_rate=dati.estimated_monthly_rate,
        initial_down_payment=dati.initial_down_payment,
        current_monthly_debts=dati.current_monthly_debts,
        has_credit_issues=dati.has_credit_issues,
        final_score=risultato["score"],
        risk_class=risultato["classe"],
        ko_reason=risultato["ko_reason"]
    )
    db.add(nuovo_report)
    db.flush()  # Genera l'ID del report per la chiave esterna
    
    # Salvataggio record verticale (profile_privati)
    dettaglio_privato = models.ProfilePrivato(
        report_id=nuovo_report.id,
        birth_date=str(dati.birth_date),
        contract_type=dati.contract_type,
        employment_start_date=str(dati.employment_start_date),
        employer_sector=dati.employer_sector,
        net_monthly_income=dati.net_monthly_income
    )
    db.add(dettaglio_privato)
    db.commit()
    
    # Preparazione e Generazione del PDF compilato
    report_data_for_pdf = {
        "user_email": dati.user_email,
        "product_type": dati.product_type,
        "target_profile": dati.target_profile,
        "contract_duration_months": dati.contract_duration_months,
        "estimated_monthly_rate": dati.estimated_monthly_rate,
        "initial_down_payment": dati.initial_down_payment,
        "final_score": risultato["score"],
        "risk_class": risultato["classe"],
        "ko_reason": risultato["ko_reason"],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    percorso_pdf = pdf_generator.genera_pdf_report(
        report_id=nuovo_report.id, 
        dati_report=report_data_for_pdf, 
        sub_scores=risultato["sub_scores"]
    )
    
    risultato["pdf_generato"] = percorso_pdf
    return risultato

# ==========================================
# 2. ENDPOINT PROFESSIONISTA (P.IVA)
# ==========================================
@app.post("/score/professionista")
def score_professionista(dati: schemas.ProfessionistaRequest, db: Session = Depends(get_db)):
    payload = dati.model_dump()
    
    # Calcolo del punteggio tramite il motore algoritmico
    risultato = engine.calcola_scoring(payload)
    
    # Salvataggio record principale (scoring_reports)
    nuovo_report = models.ScoringReport(
        user_email=dati.user_email,
        target_profile=dati.target_profile,
        product_type=dati.product_type,
        contract_duration_months=dati.contract_duration_months,
        estimated_monthly_rate=dati.estimated_monthly_rate,
        initial_down_payment=dati.initial_down_payment,
        current_monthly_debts=dati.current_monthly_debts,
        has_credit_issues=dati.has_credit_issues,
        final_score=risultato["score"],
        risk_class=risultato["classe"],
        ko_reason=risultato["ko_reason"]
    )
    db.add(nuovo_report)
    db.flush()
    
    # Salvataggio record verticale (profile_professionisti)
    dettaglio_prof = models.ProfileProfessionista(
        report_id=nuovo_report.id,
        vat_start_date=str(dati.vat_start_date),
        tax_regime=dati.tax_regime,
        ateco_code=dati.ateco_code,
        net_profit_year_n1=dati.net_profit_year_n1,
        net_profit_year_n2=dati.net_profit_year_n2
    )
    db.add(dettaglio_prof)
    db.commit()
    
    # Preparazione e Generazione del PDF compilato
    report_data_for_pdf = {
        "user_email": dati.user_email,
        "product_type": dati.product_type,
        "target_profile": dati.target_profile,
        "contract_duration_months": dati.contract_duration_months,
        "estimated_monthly_rate": dati.estimated_monthly_rate,
        "initial_down_payment": dati.initial_down_payment,
        "final_score": risultato["score"],
        "risk_class": risultato["classe"],
        "ko_reason": risultato["ko_reason"],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    percorso_pdf = pdf_generator.genera_pdf_report(
        report_id=nuovo_report.id, 
        dati_report=report_data_for_pdf, 
        sub_scores=risultato["sub_scores"]
    )
    
    risultato["pdf_generato"] = percorso_pdf
    return risultato

# ==========================================
# 3. ENDPOINT PENSIONATO
# ==========================================
@app.post("/score/pensionato")
def score_pensionato(dati: schemas.PensionatoRequest, db: Session = Depends(get_db)):
    payload = dati.model_dump()
    
    # Calcolo del punteggio tramite il motore algoritmico
    risultato = engine.calcola_scoring(payload)
    
    # Salvataggio record principale (scoring_reports)
    nuovo_report = models.ScoringReport(
        user_email=dati.user_email,
        target_profile=dati.target_profile,
        product_type=dati.product_type,
        contract_duration_months=dati.contract_duration_months,
        estimated_monthly_rate=dati.estimated_monthly_rate,
        initial_down_payment=dati.initial_down_payment,
        current_monthly_debts=dati.current_monthly_debts,
        has_credit_issues=dati.has_credit_issues,
        final_score=risultato["score"],
        risk_class=risultato["classe"],
        ko_reason=risultato["ko_reason"]
    )
    db.add(nuovo_report)
    db.flush()
    
    # Salvataggio record verticale (profile_pensionati)
    dettaglio_pens = models.ProfilePensionato(
        report_id=nuovo_report.id,
        birth_date=str(dati.birth_date),
        pension_institution=dati.pension_institution,
        net_monthly_pension=dati.net_monthly_pension,
        assigned_fifth_amount=dati.assigned_fifth_amount
    )
    db.add(dettaglio_pens)
    db.commit()
    
    # Preparazione e Generazione del PDF compilato
    report_data_for_pdf = {
        "user_email": dati.user_email,
        "product_type": dati.product_type,
        "target_profile": dati.target_profile,
        "contract_duration_months": dati.contract_duration_months,
        "estimated_monthly_rate": dati.estimated_monthly_rate,
        "initial_down_payment": dati.initial_down_payment,
        "final_score": risultato["score"],
        "risk_class": risultato["classe"],
        "ko_reason": risultato["ko_reason"],
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    percorso_pdf = pdf_generator.genera_pdf_report(
        report_id=nuovo_report.id, 
        dati_report=report_data_for_pdf, 
        sub_scores=risultato["sub_scores"]
    )
    
    risultato["pdf_generato"] = percorso_pdf
    return risultato
    