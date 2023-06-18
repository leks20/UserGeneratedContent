import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from models.bookmarks import BookmarkReqDTO, BookmarksResponseModel
from services.bookmark_service import (
    Bookmark,
    BookmarkAlreadyExists,
    BookmarkCreateDTO,
    BookmarkNotFound,
    BookmarkService,
    get_bookmark_service,
)
from utils.auth import get_current_user
from webapp.v0.api.errors import BookmarksHTTPErrors

router = APIRouter()


@router.post('/bookmarks/')
async def add_bookmark(
    movie_id: BookmarkReqDTO,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    user_id: uuid.UUID = Depends(get_current_user),
):
    movie_id = movie_id.movie_id
    bookmark_dto = BookmarkCreateDTO(movie_id=movie_id, user_id=user_id)
    try:
        await bookmark_service.add_bookmark(bookmark_dto)
    except BookmarkAlreadyExists:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=BookmarksHTTPErrors.BookmarkAlreadyExists.value.format(
                movie_id=movie_id
            ),
        )
    return {'message': f'Bookmark for movie {movie_id} has added'}


@router.get('/bookmarks/')
async def get_bookmarks(
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    user_id: uuid.UUID = Depends(get_current_user),
) -> list[BookmarksResponseModel]:
    user_bookmarks = await bookmark_service.get_user_bookmarks(user_id)
    return user_bookmarks


@router.delete('/bookmarks/{movie_id}')
async def remove_bookmark(
    movie_id: UUID4,
    bookmark_service: BookmarkService = Depends(get_bookmark_service),
    user_id: UUID4 = Depends(get_current_user),
):
    bookmark_del_dto = Bookmark(movie_id=str(movie_id), user_id=str(user_id))
    try:
        await bookmark_service.remove_bookmark(bookmark_del_dto)
    except BookmarkNotFound:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=BookmarksHTTPErrors.BookmarkNotFound.value.format(movie_id=movie_id),
        )
    return {'message': f'Bookmark for movie {movie_id} has removed'}
