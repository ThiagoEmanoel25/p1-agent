# p1-agent

Agent com uma tool de clima (`get_weather`) e um chat em SSE.
Backend em FastAPI + LangGraph, front em Vite + React + TypeScript.

## Pre-requisitos

- Python 3.13 (venv em `backend/.venv`)
- Node 20+
- Uma chave da OpenAI

## Configuracao

Crie o `.env` na **raiz** do repositorio (ele esta no `.gitignore`):

```
OPENAI_API_KEY=sk-...
```

## Subir a API

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Sobe em `http://127.0.0.1:8000`. Health check em `/health`, docs em `/docs`.

Instalacao das dependencias, se a venv ainda nao existir:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
```

## Subir o front

Em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Sobe em `http://localhost:5173`. O `vite.config.ts` faz proxy de `/agent`
para `http://127.0.0.1:8000`, entao o front chama a API na mesma origem e
nao ha CORS para configurar.

## Teste de fumaca

Com os dois no ar, abra `http://localhost:5173` e pergunte:

> Qual o clima em Sao Paulo?

Voce deve ver quatro estados na timeline, nessa ordem:

1. a tool call que o modelo decidiu fazer -- `get_weather({"city": "Sao Paulo"})`
2. o resultado do stub -- `{"city": "Sao Paulo", "temp_c": 22, "condition": "parcialmente nublado"}`
3. o texto final sendo pintado token a token (rascunho, borda tracejada)
4. o texto final consolidado pelo `on_chat_model_end` (borda dourada)

Sem o front, direto na API:

```powershell
curl.exe -N -X POST http://127.0.0.1:8000/agent/execute `
  -H "Content-Type: application/json" `
  -d '{\"message\":\"Qual o clima em Sao Paulo?\"}'
```

## Estrutura

```
backend/app/
  main.py            FastAPI, carrega o .env da raiz e registra o router
  api/routes.py      POST /agent/execute -> text/event-stream
  agent/agent.py     roda o grafo via astream_events(version="v2")
  agent/graph.py     StateGraph: no de modelo + no de tools, loop ReAct
  agent/tools.py     get_weather(city) -- stub, sleep 2s
frontend/src/
  sse.ts             fetch + ReadableStream, parser do protocolo SSE
  renderers.ts       evento -> renderer (on_chat_model_* / on_tool_*)
  types.ts           StreamEvent e os blocos da timeline
  App.tsx            estado da conversa e pintura
```

O front precisa fazer o parse do SSE na mao porque o `EventSource` nativo do
browser so faz GET, e a rota exige `POST` com body JSON.
