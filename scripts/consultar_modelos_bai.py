#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.b.ai/v1"
ENV_FILE = Path("/etc/agente-juridico-correcao.env")


def carregar_configuracao() -> dict[str, str]:
    if not ENV_FILE.is_file():
        raise RuntimeError(
            f"Arquivo de configuração não encontrado: {ENV_FILE}"
        )

    configuracao = {}

    for linha in ENV_FILE.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()

        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        chave, valor = linha.split("=", 1)
        configuracao[chave.strip()] = valor.strip().strip("\"'")

    if not configuracao.get("BAI_API_KEY"):
        raise RuntimeError("BAI_API_KEY não está configurada.")

    return configuracao


def requisitar(
    caminho: str,
    api_key: str,
    payload: dict | None = None,
) -> dict:
    dados = None
    metodo = "GET"

    if payload is not None:
        dados = json.dumps(payload).encode("utf-8")
        metodo = "POST"

    requisicao = urllib.request.Request(
        f"{API_BASE}{caminho}",
        data=dados,
        method=metodo,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(
            requisicao,
            timeout=60,
        ) as resposta:
            return json.loads(
                resposta.read().decode("utf-8")
            )
    except urllib.error.HTTPError as erro:
        corpo = erro.read().decode(
            "utf-8",
            errors="replace",
        )

        try:
            detalhes = json.loads(corpo)
        except json.JSONDecodeError:
            detalhes = {"resposta": corpo}

        raise RuntimeError(
            f"HTTP {erro.code}: "
            f"{json.dumps(detalhes, ensure_ascii=False)}"
        ) from erro
    except (urllib.error.URLError, TimeoutError) as erro:
        raise RuntimeError(
            f"Falha de conexão: {erro}"
        ) from erro


def listar_modelos(api_key: str) -> None:
    dados = requisitar("/models", api_key)
    modelos = dados.get("data", [])

    if not modelos:
        print(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    print(f"Total de modelos: {len(modelos)}\n")

    for modelo in modelos:
        print(modelo.get("id", "identificador ausente"))


def testar_modelo(
    api_key: str,
    modelo: str,
) -> None:
    dados = requisitar(
        "/chat/completions",
        api_key,
        {
            "model": modelo,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Responda somente com: "
                        "MODELO DISPONÍVEL"
                    ),
                }
            ],
            "stream": False,
            "temperature": 0.1,
            "max_tokens": 100,
        },
    )

    try:
        conteudo = dados[
            "choices"
        ][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        print(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2,
            )
        )
        raise RuntimeError(
            "Resposta recebida em formato inesperado."
        )

    print(f"OK: {modelo}")
    print(f"Resposta: {conteudo}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Lista e testa os modelos disponíveis "
            "na API da B.AI."
        )
    )
    parser.add_argument(
        "--testar",
        metavar="MODELO",
        help="Testa o acesso a um modelo específico.",
    )
    argumentos = parser.parse_args()

    try:
        configuracao = carregar_configuracao()
        api_key = configuracao["BAI_API_KEY"]

        if argumentos.testar:
            testar_modelo(
                api_key,
                argumentos.testar,
            )
        else:
            listar_modelos(api_key)

        return 0
    except RuntimeError as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
