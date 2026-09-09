import asyncio

from langchain_core.tools import tool

@tool
async def get_weather(Location:str) -> dict:
    """
    Retornamos o clima atual para determinada sociedade.
    """
    # Simulate an asynchronous API call to get weather data
    await asyncio.sleep(2)  # Simulating network delay


    return {
        "location": Location,
        "temperature": 25,
        "humidity": 60,
        "condition": "ensolarado"
    }
