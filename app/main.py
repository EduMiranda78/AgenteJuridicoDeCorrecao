import time
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.utils import extract_text_from_doc
from app.agent import AgenteJuridico

app = FastAPI()
templates = Jinja2Templates(directory="templates")

with open("prompts/system_juridico.txt", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

agente = AgenteJuridico(SYSTEM_PROMPT)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analisar", response_class=HTMLResponse)
async def analisar(request: Request, file: UploadFile = File(...)):
    inicio = time.time()
    conteudo = extract_text_from_doc(file)
    resultado = agente.analisar_gemini(conteudo)
    tempo_total = round(time.time() - inicio, 2)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "resultado": resultado,
            "tempo": tempo_total,
            "engine_usada": "GEMINI"
        }
    )
