from contextlib import asynccontextmanager

from fastapi import FastAPI

from prisma import Prisma

prisma = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await prisma.connect()
    yield
    # Clean up the ML models and release the resources
    if prisma.is_connected():
        await prisma.disconnect()
