from enum import Enum


class BookmarksHTTPErrors(str, Enum):
    BookmarkAlreadyExists = 'bookmark for movie {movie_id} is already exists'
    BookmarkNotFound = 'bookmark for movie {movie_id} has not found'


class RatingsHTTPErrors(str, Enum):
    RatingAlreadyExists = 'rating for movie {movie_id} is already exists'
    RatingNotFound = 'rating for movie {movie_id} has not found'
    RatingHasSameValue = 'rating for movie {movie_id} has the same value'


class ReviewsHTTPErrors(str, Enum):
    ReviewAlreadyExists = 'review for movie {movie_id} is already exists'
    ReviewNotFound = 'review for movie {movie_id} has not found'
