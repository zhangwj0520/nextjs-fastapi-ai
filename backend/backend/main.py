# from dotenv import load_dotenv
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from backend.api.mian import api_router

from backend.core.initPrisma import lifespan

def app() -> None:
    app = FastAPI(
        title="Gen UI Backend",
        version="1.0",
        description="A simple api server using Langchain's Runnable interfaces",
        lifespan=lifespan,
    )

    # Configure CORS
    origins = [
        "http://localhost",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # graph = create_graph()

    # runnable = graph.with_types(input_type=ChatInputType, output_type=dict)

    # add_routes(app, runnable, path="/chat", playground_type="chat")

    app.include_router(api_router, prefix="/api")

    print("Starting server...")
    # uvicorn.run(app, host="0.0.0.0", port=8100)
    return app
