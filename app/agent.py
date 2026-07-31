from __future__ import annotations

import os

import google.generativeai as genai


class AgentConfigurationError(RuntimeError):
    """Indica que o agente não possui configuração suficiente para executar."""


class AgenteJuridico:
    def __init__(
        self,
        system_prompt: str,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._model = None

    def _obter_modelo(self):
        if not self.api_key:
            raise AgentConfigurationError(
                "A variável GOOGLE_API_KEY não foi configurada no servidor."
            )

        if self._model is None:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(self.model_name)

        return self._model

    def analisar_gemini(self, texto: str) -> str:
        texto = texto.strip()
        if not texto:
            raise ValueError("O contrato não contém texto legível para análise.")

        prompt_final = self.system_prompt.format(texto_do_contrato=texto)
        resposta = self._obter_modelo().generate_content(prompt_final)
        conteudo = getattr(resposta, "text", "").strip()

        if not conteudo:
            raise RuntimeError("O Gemini não retornou conteúdo para o contrato enviado.")

        return conteudo
