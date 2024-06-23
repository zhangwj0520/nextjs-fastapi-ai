import uvicorn

# from gen_ui_backend.main import app


def start() -> None:
    print("Starting server...")
    uvicorn.run(app="backend.main:app", host="0.0.0.0", port=8100, reload=True)
