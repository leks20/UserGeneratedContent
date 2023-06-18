from pydantic import UUID4, BaseModel


class MovieModel(BaseModel):
    movie_id: UUID4
