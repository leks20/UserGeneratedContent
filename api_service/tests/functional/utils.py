import json
import os
from datetime import datetime

from pydantic import UUID4, BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTDATA_DIR = os.path.join(BASE_DIR, 'testdata')

USER_TOKEN = os.path.join(TESTDATA_DIR, 'users', 'base.user')

ADD_NEW_BOOKMARK = os.path.join(TESTDATA_DIR, 'add_new_bookmark.json')
BOOKMARKS = os.path.join(TESTDATA_DIR, 'bookmarks.json')


def load_data(filename: str):
    with open(filename, 'r') as f:
        return f.read()


def get_user_token():
    return load_data(USER_TOKEN)


def get_bookmark_from_file():
    with open(ADD_NEW_BOOKMARK, 'r') as f:
        return json.load(f)


class BookmarkRepr(BaseModel):
    movie_id: UUID4
    user_id: UUID4
    created_at: datetime


def get_fake_bookmarks():
    with open(BOOKMARKS, 'r') as f:
        return [BookmarkRepr(**bookmark) for bookmark in json.load(f)]


REVIEWS = os.path.join(TESTDATA_DIR, 'reviews.json')
REVIEW_FILE = os.path.join(TESTDATA_DIR, 'add_new_review.json')


def get_review_from_file():
    with open(REVIEW_FILE, 'r') as f:
        return json.load(f)


class ReviewRepr(BaseModel):
    movie_id: UUID4
    user_id: UUID4
    text: str
    like_count: int = 0
    dislike_count: int = 0
    users_liked: list[UUID4] = []
    users_disliked: list[UUID4] = []


def get_fake_reviews():
    with open(REVIEWS, 'r') as f:
        return [ReviewRepr(**review) for review in json.load(f)]
