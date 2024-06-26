from fastapi import APIRouter, Depends, HTTPException

from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json, uvicorn
from asyncio import sleep

from backend.ai.agent.fastapi import stream_test
from backend.ai.agent.function_calling import function_calling_demo

router = APIRouter()


# @router.get("")
# def read_root():
#     return {"Hello": "Worldnihao"}


async def waypoints_generator():
    waypoints = [
        {"lat": 22.09769, "lng": 87.24068},
        {"lat": 22.09776, "lng": 87.24075},
        {"lat": 22.09784, "lng": 87.24082},
        {"lat": 22.09811, "lng": 87.24098},
    ]
    for waypoint in waypoints[0:10]:
        data = json.dumps(waypoint)
        # yield f"event: locationUpdate\ndata: {data}\n\n"
        yield f"data: {data}\n\n"
        await sleep(1)


@router.get("")
async def root():
    # return StreamingResponse(waypoints_generator(), media_type="text/event-stream")
    return StreamingResponse(function_calling_demo(), media_type="text/event-stream")
