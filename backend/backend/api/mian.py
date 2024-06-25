from fastapi import APIRouter
from backend.api.routes import demo, prisma

from langserve import add_routes
from backend.ai.chain import create_graph
from backend.ai.types import ChatInputType


from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


api_router = APIRouter()

graph = create_graph()

runnable = graph.with_types(input_type=ChatInputType, output_type=dict)

add_routes(api_router, runnable, path="/chat", playground_type="chat")


api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(prisma.router, prefix="/prisma", tags=["prisma"])
