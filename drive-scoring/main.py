from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from pdf_generator import create_premium_pdf
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Drive Scoring API online"}

@app.post("/score/premium")
async def generate_pdf(first_name: str = Form(...), last_name: str = Form(...)):
    # Genera il PDF tramite la funzione dedicata
    pdf_bytes = create_premium_pdf(first_name, last_name)
    
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Report_Premium.pdf"}
    )
