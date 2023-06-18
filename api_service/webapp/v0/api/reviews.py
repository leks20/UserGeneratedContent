import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.reviews import ReviewCreateReqDTO, ReviewDTO
from services.review_service import (
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
    ReviewService,
    UserAlreadyDislikedError,
    UserAlreadyLikedError,
    get_review_service,
)
from utils.auth import get_current_user
from webapp.v0.api.errors import ReviewsHTTPErrors

router = APIRouter()


@router.post('/reviews/')
async def create_review(
    review_create_dto: ReviewCreateReqDTO,
    review_service: ReviewService = Depends(get_review_service),
    user_id: uuid.UUID = uuid.uuid4(),
):
    review_dto = ReviewDTO(**review_create_dto.dict(), user_id=user_id)

    try:
        await review_service.add_review(review_dto)
    except ReviewAlreadyExistsError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=ReviewsHTTPErrors.ReviewAlreadyExists.value.format(
                movie_id=review_dto.movie_id
            ),
        )

    return {'message': f'Review for movie {review_dto.movie_id} has been added'}


@router.patch('/reviews/{review_id}/like')
async def like_review(
    review_id: str,
    review_service: ReviewService = Depends(get_review_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    try:
        await review_service.add_like_to_review(review_id, user_id)
    except (ReviewNotFoundError, UserAlreadyLikedError) as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    return {'message': f'Like has been added to review {review_id}'}


@router.patch('/reviews/{review_id}/dislike')
async def dislike_review(
    review_id: str,
    review_service: ReviewService = Depends(get_review_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    try:
        await review_service.add_dislike_to_review(review_id, user_id)
    except (ReviewNotFoundError, UserAlreadyDislikedError) as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    return {'message': f'Dislike has been added to review {review_id}'}


@router.get('/reviews/')
async def get_reviews(
    sort_by: str | None = None,
    review_service: ReviewService = Depends(get_review_service),
):
    reviews = await review_service.get_reviews(sort_by)
    return {'reviews': reviews}
