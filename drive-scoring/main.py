from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from weasyprint import HTML
import io

app = FastAPI()

# Aggiungi un endpoint di test per verificare che il server sia vivo
@app.get("/")
def read_root():
    return {"status": "ok"}

# La tua rotta POST deve essere definita esattamente così
@app.post("/score/premium")
async def generate_pdf(
    first_name: str = Form(...),
    last_name: str = Form(...)
):
    # ... la tua logica ...
    return StreamingResponse(...)
