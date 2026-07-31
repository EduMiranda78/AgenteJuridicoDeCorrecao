<div align="center">

# Agente Jurídico

Ferramenta interna em FastAPI para revisar contratos com apoio do Google Gemini e produzir relatórios estruturados para a Sanar Contábil S/C Ltda.

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-2447A8?logo=google&logoColor=white)
![Tests](https://img.shields.io/badge/Testes-unittest-147A52)

</div>

> O relatório gerado é um apoio operacional. Ele não substitui parecer jurídico, revisão de advogado ou validação das condições específicas do contrato.

## Visão geral

O Agente Jurídico recebe contratos em `.doc` ou `.docx`, extrai o texto e envia o conteúdo à API do Google Gemini. O modelo segue um prompt interno para produzir quatro blocos:

1. riscos jurídicos;
2. erros formais;
3. cláusulas revisadas;
4. pontos para validação humana.

A interface permite copiar o relatório em texto simples, reduzindo o risco de execução de HTML retornado pelo modelo.

## Funcionalidades

- Upload de contratos nos formatos DOC e DOCX.
- Limite de arquivo de 10 MB.
- Extração de parágrafos e tabelas de arquivos DOCX.
- Suporte opcional a arquivos DOC por meio do `antiword`.
- Análise com Google Gemini.
- Modelo configurável por variável de ambiente.
- Relatório estruturado conforme o padrão da Sanar Contábil.
- Botão para copiar o conteúdo do relatório.
- Interface responsiva para desktop e celular.
- Healthcheck em `/health`.
- Cabeçalhos HTTP de segurança.
- Respostas com `Cache-Control: no-store`.
- Escape automático do conteúdo retornado pela IA.
- Testes automatizados sem chamadas ao serviço externo.
- GitHub Actions para execução da suíte de testes.

## Aviso de confidencialidade

O texto do contrato é enviado para um serviço externo, o Google Gemini. Antes de usar a aplicação, confirme:

- autorização para processar o documento em serviço de IA;
- regras internas de confidencialidade e proteção de dados;
- necessidade de anonimizar dados pessoais, financeiros ou estratégicos;
- política de retenção e uso de dados aplicável à conta da API.

Não exponha esta aplicação publicamente sem autenticação, HTTPS, controle de acesso e limitação de requisições.

## Segurança da chave de API

A chave do Gemini deve existir somente como variável de ambiente no servidor.

Se uma chave já foi gravada em um commit, removê-la do arquivo atual não é suficiente. A chave continua no histórico Git e precisa ser revogada no Google, com emissão de uma nova credencial.

Nunca publique a nova chave no repositório, em prints, logs, issues ou pull requests.

## Tecnologias

- Python 3.12 ou superior
- FastAPI
- Uvicorn
- Jinja2
- python-docx
- Google Generative AI SDK
- python-multipart
- HTML, CSS e JavaScript

## Estrutura principal

```text
agente_juridico/
├── .github/
│   └── workflows/
│       └── tests.yml
├── app/
│   ├── agent.py
│   ├── main.py
│   └── utils.py
├── prompts/
│   └── system_juridico.txt
├── static/
│   ├── app.js
│   └── styles.css
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Requisitos

- Python 3.12 ou superior
- `pip`
- Chave válida da API do Google Gemini
- `antiword`, somente para contratos antigos no formato `.doc`

No Debian e Ubuntu, o suporte a `.doc` pode ser instalado com:

```bash
sudo apt update
sudo apt install antiword
```

Arquivos `.docx` não exigem `antiword`.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/EduMiranda78/agente_juridico.git
cd agente_juridico
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuração

A aplicação lê estas variáveis:

| Variável | Obrigatória | Padrão | Finalidade |
| --- | --- | --- | --- |
| `GOOGLE_API_KEY` | Sim | Nenhum | Autenticação na API do Gemini |
| `GEMINI_MODEL` | Não | `gemini-2.5-flash` | Modelo usado para gerar o relatório |

Exporte as variáveis no Linux:

```bash
export GOOGLE_API_KEY="sua_nova_chave_do_gemini"
export GEMINI_MODEL="gemini-2.5-flash"
```

No Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY="sua_nova_chave_do_gemini"
$env:GEMINI_MODEL="gemini-2.5-flash"
```

O arquivo `.env.example` serve apenas como referência. A aplicação não carrega arquivos `.env` automaticamente. Use variáveis do sistema, do serviço ou do contêiner.

## Execução local

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse:

```text
http://127.0.0.1:8000
```

Para reinício automático durante desenvolvimento:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Não use `--reload` em produção.

## Como usar

1. Abra a página inicial.
2. Leia o aviso de confidencialidade.
3. Selecione um contrato `.doc` ou `.docx` de até 10 MB.
4. Clique em **Analisar com Gemini**.
5. Revise riscos, erros formais, cláusulas sugeridas e pontos para validação humana.
6. Use **Copiar relatório** somente depois da conferência.

## Endpoints

| Método | Caminho | Finalidade |
| --- | --- | --- |
| `GET` | `/` | Interface de upload e relatório |
| `POST` | `/analisar` | Processamento do contrato |
| `GET` | `/health` | Verificação de disponibilidade |
| `GET` | `/docs` | Documentação automática do FastAPI |

Verifique o serviço:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Resposta esperada:

```json
{"status":"ok"}
```

## Testes

Execute a suíte:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem:

- carregamento da página inicial;
- entrega dos arquivos estáticos;
- healthcheck;
- rejeição de extensões não permitidas;
- processamento de DOCX sem acesso ao Gemini;
- escape de HTML retornado pelo modelo;
- cabeçalhos HTTP de segurança.

O workflow `.github/workflows/tests.yml` executa a mesma suíte em pushes para `main`, branches `agent/**` e pull requests destinados à `main`.

## Proteções aplicadas

- A chave do Gemini não fica no código.
- O nome original do upload não é usado como caminho no servidor.
- Arquivos temporários são removidos após a extração.
- Uploads acima de 10 MB são recusados.
- O formato do arquivo é validado antes da leitura.
- O processamento de `.doc` possui limite de tempo.
- Erros internos são registrados no servidor sem detalhes técnicos na página.
- O conteúdo produzido pelo Gemini é exibido como texto escapado.
- A política de conteúdo permite apenas recursos locais.
- As páginas não devem ser armazenadas em cache.
- A aplicação solicita que mecanismos de busca não indexem o conteúdo.

## Implantação

Para uso interno em servidor:

- execute o Uvicorn como serviço dedicado;
- use Nginx como proxy reverso;
- ative HTTPS;
- restrinja o acesso por VPN, rede interna ou autenticação;
- limite tamanho, frequência e duração das requisições;
- mantenha logs sem o conteúdo integral dos contratos;
- armazene a chave em variável de ambiente ou cofre de segredos.

## Limitações

- A IA pode omitir riscos ou interpretar cláusulas de forma incorreta.
- O relatório depende da qualidade do texto extraído.
- Documentos digitalizados como imagem podem não conter texto legível.
- O sistema não consulta legislação ou jurisprudência em tempo real.
- O modelo não conhece anexos que não foram enviados.
- O resultado exige revisão humana antes de qualquer uso jurídico.

## Melhorias previstas

- Autenticação de usuários.
- Registro de auditoria sem armazenar o conteúdo contratual.
- Suporte controlado a PDF com extração segura.
- Rate limiting.
- Métricas de uso e falhas.
- Containerização com Docker.
- Configuração pronta para Nginx e serviço `systemd`.
- Migração para o SDK mais recente do Google quando planejada e testada.

## Autor

Desenvolvido por [Eduardo Miranda](https://github.com/EduMiranda78) para uso interno da Sanar Contábil S/C Ltda.

## Licença

Este repositório ainda não possui uma licença definida. Até que uma licença seja adicionada, o código permanece protegido pelos direitos autorais do autor.
