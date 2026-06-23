"""Progress API routes."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.models import User

router = APIRouter()


class ProgressResponse(BaseModel):
    total_reviews: int
    correct_reviews: int
    accuracy: float
    current_streak: int
    longest_streak: int
    xp: int
    level: int


def _build_progress_response(user: User) -> ProgressResponse:
    p = user.progress
    if not p:
        return ProgressResponse(
            total_reviews=0, correct_reviews=0, accuracy=0,
            current_streak=0, longest_streak=0, xp=0, level=1,
        )
    total = p.total_reviews or 0
    correct = p.correct_reviews or 0
    accuracy = (correct / total * 100) if total > 0 else 0
    return ProgressResponse(
        total_reviews=total,
        correct_reviews=correct,
        accuracy=round(accuracy, 1),
        current_streak=p.current_streak or 0,
        longest_streak=p.longest_streak or 0,
        xp=p.xp or 0,
        level=p.level or 1,
    )


@router.get("/", response_model=ProgressResponse)
async def get_progress(user: User = Depends(get_current_user)):
    return _build_progress_response(user)


@router.get("", response_model=ProgressResponse)
async def get_progress_no_slash(user: User = Depends(get_current_user)):
    return _build_progress_response(user)
