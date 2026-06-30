from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

# 1. Dati comuni a qualsiasi richiesta
class BaseReportRequest(BaseModel):
    user_email: str  # La mail per ricevere il PDF
    target_profile: str  # PRIVATO, PROFESSIONISTA, PENSIONATO
    product_type: str  # NOLEGGIO, LEASING, FINANZIAMENTO
    contract_duration_months: int
    estimated_monthly_rate: float
    initial_down_payment: float = 0.0
    current_monthly_debts: float = 0.0
    has_credit_issues: bool  # Autodichiarazione ritardi/segnalazioni

# 2. Dati specifici per il Privato (Dipendente)
class PrivatoRequest(BaseReportRequest):
    birth_date: date
    contract_type: str  # INDETERMINATO, DETERMINATO, APPRENDISTATO
    employment_start_date: date
    employer_sector: str  # PUBBLICO, PRIVATO_SPA_SRL, PRIVATO_MINORE
    net_monthly_income: float

# 3. Dati specifici per il Professionista (Partita IVA)
class ProfessionistaRequest(BaseReportRequest):
    vat_start_date: date
    tax_regime: str  # FORFETTARIO, ORDINARIO
    ateco_code: str
    net_profit_year_n1: float  # Utile ultimo anno
    net_profit_year_n2: float  # Utile anno precedente

# 4. Dati specifici per il Pensionato
class PensionatoRequest(BaseReportRequest):
    birth_date: date
    pension_institution: str  # INPS_STANDARD, CASSA_PROF, ASSISTENZIALE
    net_monthly_pension: float
    assigned_fifth_amount: float = 0.0  # Cessione del quinto eventual