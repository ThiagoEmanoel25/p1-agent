import asyncio

from langchain_core.tools import tool


@tool
async def get_weather(city: str) -> dict:
    """Retorna o clima atual de uma cidade.

    Use sempre que o usuario perguntar sobre clima, tempo, temperatura
    ou condicoes meteorologicas de um lugar.
    """
    # Stub: sem HTTP, so simula a latencia de uma API real.
    await asyncio.sleep(2)

    return {
        "city": city,
        "temp_c": 22,
        "condition": "parcialmente nublado",
    }
