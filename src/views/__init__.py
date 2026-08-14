"""Telas e registro central das rotas do Sejong Companion."""

from .hangul_view import hangul_view
from .home_view import home_view
from .lesson_view import lesson_view
from .quiz_view import quiz_view
from .splash_view import splash_view
from .review_view import review_view
from .flashcards_view import flashcards_view

APP_ROUTES = {
    "/splash": splash_view,
    "/home": home_view,
    "/hangul": hangul_view,
    "/lesson": lesson_view,
    "/quiz": quiz_view,
    "/review": review_view,
    "/flashcards": flashcards_view,
}

__all__ = ["APP_ROUTES", "hangul_view", "home_view", "lesson_view", "quiz_view", "splash_view", "review_view", "flashcards_view"]
