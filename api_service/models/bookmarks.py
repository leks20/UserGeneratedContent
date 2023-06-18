import datetime

from models.base import MovieModel


class BookmarkReqDTO(MovieModel):
    pass


class BookmarksResponseModel(MovieModel):
    created_at: datetime.datetime
