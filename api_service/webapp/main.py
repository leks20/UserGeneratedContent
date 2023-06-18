import sentry_sdk
from fastapi import APIRouter, FastAPI
from prometheus_client import generate_latest
from starlette.responses import Response

from conf.config import settings
from utils.kafka.producer import create_and_start_producer, stop_producer
from utils.metrics import start_mem_monitoring, stop_mem_monitoring
from utils.mongo import connect_to_mongo
from utils.redis import connect_to_redis, stop_redis
from webapp.v0.api.bookmarks import router as bookmarks_router
from webapp.v0.api.progress import router as progress_router
from webapp.v0.api.ratings import router as ratings_router
from webapp.v0.api.reviews import router as reviews_router
from webapp.v0.api.user import API_VERSION_MAJOR, router as user_router

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0,
)


def registration_routers(app: FastAPI):
    api_router = APIRouter()

    api_router.include_router(progress_router, tags=[f'v{API_VERSION_MAJOR}'])
    api_router.include_router(user_router, tags=[f'v{API_VERSION_MAJOR}'])
    api_router.include_router(bookmarks_router, tags=[f'v{API_VERSION_MAJOR}'])
    api_router.include_router(ratings_router, tags=[f'v{API_VERSION_MAJOR}'])
    api_router.include_router(reviews_router, tags=[f'v{API_VERSION_MAJOR}'])

    app.include_router(api_router, prefix=f'/api/v{API_VERSION_MAJOR}')


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url='/swagger',
        on_startup=[
            create_and_start_producer,
            connect_to_redis,
            connect_to_mongo,
            start_mem_monitoring,
        ],
        on_shutdown=[stop_producer, stop_redis, stop_mem_monitoring],
    )
    registration_routers(app)

    @app.get('/sentry-debug')
    async def trigger_error():
        raise

    @app.get('/metrics')
    async def prometheus_metrics():
        return Response(generate_latest())

    return app
