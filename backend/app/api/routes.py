import json

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.agent import agent


router = APIRouter()


class ExecuteRequest(BaseModel):
    message: str


async def sse_stream(message: str):
    async for stream_event in agent.execute(message):

        encoded_event = jsonable_encoder(
            stream_event
        )

        data = json.dumps(
            encoded_event,
            ensure_ascii=False,
        )

        event_name = stream_event["event"]

        yield (
            f"event: {event_name}\n"
            f"data: {data}\n\n"
        )


@router.post("/agent/execute")
async def execute_agent(body: ExecuteRequest):
    return StreamingResponse(
        sse_stream(body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )