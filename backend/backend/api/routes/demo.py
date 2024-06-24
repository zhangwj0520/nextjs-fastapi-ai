from fastapi import APIRouter, Depends, HTTPException

from typing import Union

router = APIRouter()


@router.get("")
def read_root():
    return {"Hello": "Worldnihao"}


@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
