from datetime import datetime
from typing import Literal

from bson import ObjectId
from pydantic import UUID4, Field

from models.base import MovieModel


class RatingCreateReqDTO(MovieModel):
    rating: Literal[0, 10]


class RatingDTO(RatingCreateReqDTO):
    user_id: UUID4
    created_at: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class RatingMongoDTO(RatingDTO):
    id: ObjectId = Field(alias='_id')

    class Config:
        arbitrary_types_allowed = True


class RatingDeleteDTO(MovieModel):
    user_id: UUID4
