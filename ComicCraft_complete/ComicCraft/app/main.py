from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router


def create_app() -> FastAPI:
    settings.panels_dir
    settings.exports_dir

    application = FastAPI(
        title=settings.app_name,
        description="AI comic story and illustration generator.",
        version="1.0.0",
    )

    application.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static",
    )
    application.include_router(router)

    return application


app = create_app()
