import uuid
from datetime import datetime

from bson import ObjectId
from pydantic import UUID4

from models.base import MovieModel


class ReviewCreateReqDTO(MovieModel):
    text: str


class ReviewDTO(ReviewCreateReqDTO):
    user_id: UUID4
    created_at: datetime = datetime.now()
    rating: float = 0.0


class ReviewRatingDTO(MovieModel):
    review_id: ObjectId
    user_id: UUID4
    like_count: int = 0
    dislike_count: int = 0
    users_liked: list[uuid.UUID] = []
    users_disliked: list[uuid.UUID] = []

    class Config:
        arbitrary_types_allowed = True
