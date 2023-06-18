from datetime import datetime

from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic.types import UUID4


class ProgressModel(BaseModel):
    progress: float = Field(..., ge=0, le=100)  # в процентах


class MovieWatchProgressReq(ProgressModel):
    movie_id: UUID4


class MovieWatchProgress(MovieWatchProgressReq):
    user_id: UUID4
    event_time: datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
