from __future__ import annotations

import os
from typing import Any

import httpx


class AgentConfigurationError(RuntimeError):
    """Indica que o agente não possui configuração suficiente para executar."""


class AgentServiceError(RuntimeError):
    """Indica uma falha controlada no provedor de inteligência artificial."""


class AgenteJuridico:
    API_URL = "https://api.b.ai/v1/chat/completions"

    def __init__(
        self,
        system_prompt: str,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.api_key = api_key or os.getenv("BAI_API_KEY")
        self.model_name = model_name or os.getenv("BAI_MODEL", "qwen3.8-flash")

    @staticmethod
    def _extrair_conteudo(dados: dict[str, Any]) -> str:
        try:
            conteudo = dados["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as erro:
            raise AgentServiceError(
                "A B.AI retornou uma resposta em formato inesperado."
            ) from erro

        if not isinstance(conteudo, str) or not conteudo.strip():
            raise AgentServiceError("A B.AI não retornou conteúdo para o contrato.")

        return conteudo.strip()

    async def analisar_bai(self, texto: str) -> str:
        texto = texto.strip()
        if not texto:
            raise ValueError("O contrato não contém texto legível para análise.")

        if not self.api_key:
            raise AgentConfigurationError(
                "A variável BAI_API_KEY não foi configurada no servidor."
            )

        prompt_final = self.system_prompt.format(texto_do_contrato=texto)
        timeout = httpx.Timeout(connect=10.0, read=180.0, write=30.0, pool=10.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as cliente:
                resposta = await cliente.post(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt_final}],
                        "stream": False,
                        "temperature": 0.1,
                        "max_tokens": 8000,
                    },
                )
        except httpx.TimeoutException as erro:
            raise AgentServiceError(
                "A análise excedeu o tempo permitido. Tente novamente."
            ) from erro
        except httpx.RequestError as erro:
            raise AgentServiceError(
                "Não foi possível comunicar com a B.AI. Tente novamente."
            ) from erro

        if resposta.status_code == 401:
            raise AgentConfigurationError("A chave da B.AI foi recusada.")
        if resposta.status_code == 429:
            raise AgentServiceError(
                "O limite de uso da conta B.AI foi atingido. Tente novamente mais tarde."
            )
        if resposta.status_code >= 500:
            raise AgentServiceError(
                "A B.AI está temporariamente indisponível. Tente novamente."
            )

        try:
            resposta.raise_for_status()
            dados = resposta.json()
        except (httpx.HTTPStatusError, ValueError) as erro:
            raise AgentServiceError(
                "A B.AI recusou a solicitação ou retornou uma resposta inválida."
            ) from erro

        return self._extrair_conteudo(dados)
