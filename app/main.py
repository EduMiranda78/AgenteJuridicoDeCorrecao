from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.agent import AgentConfigurationError, AgentServiceError, AgenteJuridico
from app.utils import extract_text_from_doc

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "system_juridico.txt"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agente Jurídico",
    description="Ferramenta interna de apoio à revisão de contratos.",
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
agente = AgenteJuridico(SYSTEM_PROMPT)


def renderizar_index(
    request: Request,
    *,
    status_code: int = status.HTTP_200_OK,
    resultado: str | None = None,
    erro: str | None = None,
    tempo: float | None = None,
    engine_usada: str | None = None,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "resultado": resultado,
            "erro": erro,
            "tempo": tempo,
            "engine_usada": engine_usada,
        },
        status_code=status_code,
    )


@app.middleware("http")
async def adicionar_cabecalhos_seguranca(request: Request, call_next):
    resposta = await call_next(request)
    resposta.headers.setdefault("Cache-Control", "no-store")
    resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
    resposta.headers.setdefault("X-Frame-Options", "DENY")
    resposta.headers.setdefault("Referrer-Policy", "no-referrer")
    resposta.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
    resposta.headers.setdefault(
        "Permissions-Policy",
        "camera=(), geolocation=(), microphone=()",
    )
    resposta.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; "
        "style-src 'self'; "
        "script-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'",
    )
    return resposta


@app.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request):
    return renderizar_index(request)


@app.post("/analisar", response_class=HTMLResponse, name="analisar")
async def analisar(
    request: Request,
    file: UploadFile = File(...),
):
    inicio = time.monotonic()

    try:
        conteudo = extract_text_from_doc(file)
        resultado = await agente.analisar_bai(conteudo)
        tempo_total = round(time.monotonic() - inicio, 2)

        return renderizar_index(
            request,
            resultado=resultado,
            tempo=tempo_total,
            engine_usada=f"B.AI / {agente.model_name}",
        )
    except ValueError as erro:
        return renderizar_index(
            request,
            status_code=status.HTTP_400_BAD_REQUEST,
            erro=str(erro),
        )
    except AgentConfigurationError:
        logger.error("A configuração da B.AI não está disponível ou foi recusada")
        return renderizar_index(
            request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            erro="O serviço de análise não está configurado. Verifique a chave da B.AI no servidor.",
        )
    except AgentServiceError as erro:
        logger.warning("Falha controlada na B.AI: %s", erro)
        return renderizar_index(
            request,
            status_code=status.HTTP_502_BAD_GATEWAY,
            erro=str(erro),
        )
    except Exception:
        logger.exception("Falha inesperada durante a análise do contrato")
        return renderizar_index(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            erro="Não foi possível concluir a análise. Verifique o arquivo e tente novamente.",
        )
    finally:
        await file.close()


@app.get("/health", name="health")
async def health():
    return {"status": "ok"}
