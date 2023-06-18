import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.base import MovieModel
from models.ratings import RatingCreateReqDTO, RatingDeleteDTO, RatingDTO
from services.rating_service import (
    RatingAlreadyExists,
    RatingNotFoundError,
    RatingService,
    SameRatingError,
    get_rating_service,
)
from utils.auth import get_current_user
from webapp.v0.api.errors import RatingsHTTPErrors

router = APIRouter()


@router.post('/ratings/')
async def add_rating(
    rating_req_dto: RatingCreateReqDTO,
    rating_service: RatingService = Depends(get_rating_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    rating_dto = RatingDTO(**rating_req_dto.dict(), user_id=user_id)
    try:
        await rating_service.add_rating(rating_dto)
    except RatingAlreadyExists:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=RatingsHTTPErrors.RatingAlreadyExists.value.format(
                movie_id=rating_dto.movie_id
            ),
        )
    return {'message': f'Rating for movie {rating_dto.movie_id} has added'}


@router.patch('/ratings/')
async def update_rating(
    rating_req_dto: RatingCreateReqDTO,
    rating_service: RatingService = Depends(get_rating_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    rating_dto = RatingDTO(**rating_req_dto.dict(), user_id=user_id)
    try:
        await rating_service.update_rating(rating_dto)
    except RatingNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=RatingsHTTPErrors.RatingNotFound.value.format(
                movie_id=rating_dto.movie_id
            ),
        )
    except SameRatingError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=RatingsHTTPErrors.RatingHasSameValue.value.format(
                movie_id=rating_dto.movie_id
            ),
        )
    return {'message': f'Rating for movie {rating_dto.movie_id} has updated'}


@router.delete('/ratings/')
async def remove_rating(
    movie_id_dto: MovieModel,
    rating_service: RatingService = Depends(get_rating_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    movie_id = movie_id_dto.movie_id
    rating_dto = RatingDeleteDTO(movie_id=movie_id, user_id=user_id)

    try:
        await rating_service.remove_rating(rating_dto)
    except RatingNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=RatingsHTTPErrors.RatingNotFound.value.format(movie_id=movie_id),
        )
    return {'message': f'Rating for movie {rating_dto.movie_id} has removed'}


@router.get('/ratings/average/')
async def get_movies_avg_rating(
    movie_id: uuid.UUID | None = None,
    rating_service: RatingService = Depends(get_rating_service),
    page: int = 1,
    limit: int = 50,
    user_id: uuid.UUID = Depends(get_current_user),
):
    result = []
    if movie_id:
        rating = await rating_service.get_movie_rating(str(movie_id))
        result.append(rating)
    else:
        result = await rating_service.get_rating_table(page, limit)

    return {'ratings': result}
