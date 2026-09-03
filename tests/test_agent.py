import json
import unittest
from unittest.mock import patch

from app.agent import (
    AgentConfigurationError,
    AgentServiceError,
    AgenteJuridico,
)


class RespostaFake:
    def __init__(self, status_code=200, dados=None):
        self.status_code = status_code
        self._dados = dados or {
            "choices": [{"message": {"content": "Relatório B.AI simulado."}}]
        }

        self.text = (
            "data: "
            + json.dumps(self._dados, ensure_ascii=False)
            + "\n\ndata: [DONE]\n"
        )

    def raise_for_status(self):
        return None

    def json(self):
        return self._dados


class ClienteFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.chamada = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, headers, json):
        self.chamada = {"url": url, "headers": headers, "json": json}
        return self.resposta


class AgenteJuridicoTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_gera_relatorio_sem_rede(self):
        cliente = ClienteFake(RespostaFake())
        agente = AgenteJuridico(
            "Analise: {texto_do_contrato}",
            api_key="chave-de-teste",
            model_name="qwen3.8-flash",
        )

        with patch("app.agent.httpx.AsyncClient", return_value=cliente):
            resultado = await agente.analisar_bai("Contrato fictício")

        self.assertEqual(resultado, "Relatório B.AI simulado.")
        self.assertEqual(cliente.chamada["json"]["stream"], True)
        self.assertEqual(cliente.chamada["json"]["temperature"], 0.1)
        self.assertIn("Contrato fictício", cliente.chamada["json"]["messages"][0]["content"])
        self.assertEqual(
            cliente.chamada["headers"]["Authorization"],
            "Bearer chave-de-teste",
        )

    async def test_exige_chave(self):
        agente = AgenteJuridico(
            "Analise: {texto_do_contrato}",
            api_key="",
        )
        agente.api_key = None

        with self.assertRaises(AgentConfigurationError):
            await agente.analisar_bai("Contrato fictício")

    async def test_rejeita_resposta_sem_conteudo(self):
        cliente = ClienteFake(RespostaFake(dados={"choices": []}))
        agente = AgenteJuridico(
            "Analise: {texto_do_contrato}",
            api_key="chave-de-teste",
        )

        with patch("app.agent.httpx.AsyncClient", return_value=cliente):
            with self.assertRaises(AgentServiceError):
                await agente.analisar_bai("Contrato fictício")


if __name__ == "__main__":
    unittest.main()
