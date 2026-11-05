from fastapi import FastAPI

from circuit_shift.presentation.health import router


def create_app() -> FastAPI:
    app = FastAPI(title="Circuit Shift", docs_url=None, redoc_url=None)
    app.include_router(router)
    return app
