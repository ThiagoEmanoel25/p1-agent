from langchain_core.messages import HumanMessage

from .graph import create_graph as create_state_graph


class Agent:
    def __init__(self):
        self.state_graph = create_state_graph()

    async def execute(self, mensage: str):
        input_state = {
            "messages": [
                HumanMessage(content=mensage)
            ]
        }


        async for event in self.state_graph.astream_events(
            input_state,
            version="v2",
            include_types=["chat_model", "tool"],

        ):
            yield event

agent = Agent()
    