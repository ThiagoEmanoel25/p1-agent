from typing import Literal 

from pydantic import BaseModel, Field

class WeatherOutput(BaseModel):
    answer: str = Field(
        description="Resposta Final do Usuário.",
    )
    city: str = Field(
        description="Nome da cidade consultada ou null.",
    )
    country: str = Field(
        description="Nome do país consultado ou null.",
    )
    temperature: float = Field(
        description="Temperatura atual da cidade consultada ou null.",
    )
    conditions: str = Field(
        description="Condições climáticas atuais da cidade consultada ou null.",
    )
    observed_at: str = Field(
        description="Data e hora da observação do clima ou null.",
    )
    source: Literal["open-meteo"] = Field(
        description="Fonte da informação climática.",
    )
    status: Literal["success", "error", "not_weather_data"] = Field(
        description="Status da resposta: 'success' para sucesso, 'error' para erro, 'not_weather_data' para dados não encontrados.",
    )
    