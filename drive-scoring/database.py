from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Definiamo dove salvare il database (un file chiamato drive_scoring.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./drive_scoring.db"

# Creiamo l'engine di connessione
engine_db = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Creiamo la sessione per fare le query (SELECT, INSERT, ecc.)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_db)

# La classe base da cui erediteranno i nostri modelli SQL
Base = declarative_base()

# Funzione di utilità per aprire e chiudere la connessione a ogni richiesta API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
