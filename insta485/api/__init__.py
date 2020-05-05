"""Insta485 REST API."""

from insta485.api.api import api
from insta485.api.likes import get_likes, like_post, dislike_post
from insta485.api.comments import get_comments, post_comment
from insta485.api.posts import get_post, get_posts
