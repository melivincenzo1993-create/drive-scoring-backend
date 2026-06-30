import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from database import Base

class ScoringReport(Base):
    __tablename__ = "scoring_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, index=True, nullable=False)
    target_profile = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    contract_duration_months = Column(Integer, nullable=False)
    estimated_monthly_rate = Column(Float, nullable=False)
    initial_down_payment = Column(Float, default=0.0)
    current_monthly_debts = Column(Float, default=0.0)
    has_credit_issues = Column(Boolean, nullable=False)
    final_score = Column(Integer, nullable=False)
    risk_class = Column(String, nullable=False)
    ko_reason = Column(String, nullable=True)
    pdf_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProfilePrivato(Base):
    __tablename__ = "profile_privati"

    report_id = Column(String, ForeignKey("scoring_reports.id", ondelete="CASCADE"), primary_key=True)
    birth_date = Column(String, nullable=False)
    contract_type = Column(String, nullable=False)
    employment_start_date = Column(String, nullable=False)
    employer_sector = Column(String, nullable=False)
    net_monthly_income = Column(Float, nullable=False)

class ProfileProfessionista(Base):
    __tablename__ = "profile_professionisti"

    report_id = Column(String, ForeignKey("scoring_reports.id", ondelete="CASCADE"), primary_key=True)
    vat_start_date = Column(String, nullable=False)
    tax_regime = Column(String, nullable=False)
    ateco_code = Column(String, nullable=False)
    net_profit_year_n1 = Column(Float, nullable=False)
    net_profit_year_n2 = Column(Float, nullable=False)

class ProfilePensionato(Base):
    __tablename__ = "profile_pensionati"

    report_id = Column(String, ForeignKey("scoring_reports.id", ondelete="CASCADE"), primary_key=True)
    birth_date = Column(String, nullable=False)
    pension_institution = Column(String, nullable=False)
    net_monthly_pension = Column(Float, nullable=False)
    assigned_fifth_amount = Column(Float, default=0.0)
    