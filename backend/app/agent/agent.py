
import json

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI

from .graph import create_graph as create_state_graph
from .schema import WeatherOutput


class Agent:

    def __init__(self):

        # Grafo original: modelo + ferramentas.
        self.state_graph = create_state_graph()

        # Modelo responsável por gerar o output estruturado.
        self.structured_model = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0,
        ).with_structured_output(
            WeatherOutput,
            method="json_schema",
        )

    async def execute(self, message: str):

        # Mensagem recebida do usuário.
        input_state = {
            "messages": [
                HumanMessage(content=message)
            ]
        }

        # Armazena a resposta final do agente.
        final_answer = ""

        # Armazena os resultados das ferramentas.
        tool_results = []

        # Executa o LangGraph normalmente.
        async for event in self.state_graph.astream_events(
            input_state,
            version="v2",
            include_types=["chat_model", "tool"],
        ):

            event_type = event["event"]

            # Captura o resultado de cada ferramenta.
            if event_type == "on_tool_end":

                output = event["data"].get("output")

                content = getattr(
                    output,
                    "content",
                    output,
                )

                tool_results.append({
                    "name": event["name"],
                    "result": content,
                })

            # Captura a resposta final do modelo.
            if event_type == "on_chat_model_end":

                output = event["data"].get("output")

                if output is not None:

                    # Uma chamada de ferramenta não é
                    # a resposta final do agente.
                    tool_calls = getattr(
                        output,
                        "tool_calls",
                        [],
                    )

                    content = getattr(
                        output,
                        "content",
                        "",
                    )

                    if not tool_calls and isinstance(
                        content,
                        str,
                    ):
                        final_answer = content

            # Mantém o streaming original do P1.
            yield event

        # Contexto enviado ao modelo formatador.
        context = {
            "user_message": message,
            "agent_answer": final_answer,
            "tool_results": tool_results,
        }

        # Gera uma resposta estruturada.
        structured_response = (
            await self.structured_model.ainvoke(
                [
                    SystemMessage(
                        content=(
                            "Você é um formatador de respostas "
                            "de um agente meteorológico. "
                            "Use os resultados das ferramentas "
                            "como fonte dos dados meteorológicos. "
                            "Não invente cidades, temperaturas, "
                            "condições, horários ou fontes. "
                            "Se a ferramenta falhou, use "
                            "status='error' e campos "
                            "meteorológicos null. "
                            "Se não houve consulta meteorológica, "
                            "use status='not_weather' e campos "
                            "meteorológicos null. "
                            "Se a consulta foi bem-sucedida, "
                            "use status='success'. "
                            "A resposta deve ser em português."
                        )
                    ),
                    HumanMessage(
                        content=json.dumps(
                            context,
                            ensure_ascii=False,
                            default=str,
                        )
                    ),
                ]
            )
        )

        # Envia um evento customizado para o frontend.
        yield {
            "event": "on_structured_output",
            "name": "structured_output",
            "run_id": "structured-output",
            "data": {
                "structured": (
                    structured_response.model_dump()
                )
            },
        }


agent = Agent()