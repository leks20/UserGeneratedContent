import logging
import uuid

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from fastapi import APIRouter, Depends

from models.progress import MovieWatchProgress, MovieWatchProgressReq, ProgressModel
from services.content_service import MovieContentService, get_movie_content_svc
from utils.auth import get_current_user
from utils.kafka.producer import get_producer

API_VERSION_MAJOR = 0
API_VERSION_MINOR = 1
API_VERSION_PATH = 0

API_VERSION = f'{API_VERSION_MAJOR}.{API_VERSION_MINOR}.{API_VERSION_PATH}'

router = APIRouter()


@router.post('/progress/')
async def track_progress(
    progress: MovieWatchProgressReq,
    producer: AIOKafkaProducer = Depends(get_producer),
    user_id: str = Depends(get_current_user),
):
    progress_dto = MovieWatchProgress(**progress.dict(), user_id=user_id)

    try:
        await producer.send_and_wait(
            topic='watch_progress',
            key=f'{user_id}:{progress.movie_id}'.encode(),
            value=progress_dto.json().encode(),
        )
    except KafkaError as exc:
        logging.exception('An error occurred while sending data to Kafka: %s', exc)
    return {'message': 'Progress tracked successfully'}


@router.get('/progress/{movie_id}', response_model=ProgressModel)
async def get_progress(
    movie_id: uuid.UUID,
    movie_svc: MovieContentService = Depends(get_movie_content_svc),
    user_id: uuid.UUID = Depends(get_current_user),
):
    progress = await movie_svc.get_movie_watching_progress(user_id, movie_id)

    return ProgressModel(progress=progress or 0)
