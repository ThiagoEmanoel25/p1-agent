import httpx

from langchain_core.tools import tool

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10.0

WEATHER_CODES = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com deposição de gelo",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa intensa",
    56: "Garoa congelante fraca",
    57: "Garoa congelante intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva forte",
    66: "Chuva congelante fraca",
    67: "Chuva congelante forte",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva fortes",
    85: "Pancadas de neve fracas",
    86: "Pancadas de neve fortes",
    95: "Tempestade",
    96: "Tempestade com granizo fraco",
    99: "Tempestade com granizo forte",
}

@tool
async def get_weather(city: str) -> dict:
    """Retorna o clima atual de uma cidade usando a api da open-meteo.

    Use sempre que o usuario perguntar sobre clima, tempo, temperatura
    ou condicoes meteorologicas de um lugar.
    """
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            # Get the coordinates of the city
            geocoding_response = await client.get(
                GEOCODING_URL,
                params={"name": city, "count": 1, "language": "pt"},
            )
            geocoding_response.raise_for_status()
            results = geocoding_response.json().get("results")
            if not results:
                return {"error": "Cidade não encontrada."}
            place = results[0]

            # Get the weather data for the coordinates
            weather_response = await client.get(
                WEATHER_URL,
                params={
                    "latitude": place["latitude"],
                    "longitude": place["longitude"],
                    "current_weather": True,
                },
            )
            weather_response.raise_for_status()
            current_weather = weather_response.json().get("current_weather")
            if not current_weather:
                return {"error": "Não foi possível obter o clima atual."}

            # Map the weather code to a description
            weather_code = current_weather.get("weathercode")
            weather_description = WEATHER_CODES.get(weather_code, "Código de clima desconhecido")

            return {
                "city": place.get("name", city),
                "temperature": current_weather.get("temperature"),
                "windspeed": current_weather.get("windspeed"),
                "weather_description": weather_description,
            }
    except httpx.HTTPError as exc:
        return {"error": f"Falha ao consultar a API de clima: {exc}"}
