from fastapi import APIRouter

from backend.api.routes import demo, prisma

from pydantic import BaseModel


from typing import Union

api_router = APIRouter()


# @api_router.get("")
# async def read_root():
#     return {"Hello": "World11122"}


# @api_router.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@api_router.post("/items")
async def create_item(item: Item):
    return item


# api_router.include_router(login.router, tags=["login"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(prisma.router, prefix="/prisma", tags=["prisma"])
