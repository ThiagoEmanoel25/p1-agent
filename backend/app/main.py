from pathlib import Path

from dotenv import load_dotenv

# Precisa rodar antes de importar as rotas: o import da cadeia
# routes -> agent -> graph instancia o ChatOpenAI, que le OPENAI_API_KEY.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(title="p1-agent")

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
