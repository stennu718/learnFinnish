"""SRS (Spaced Repetition) API routes."""
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, SRSCard, WordPair, UserProgress
from app.services.srs import calculate_sm2

router = APIRouter()


class DueCardResponse(BaseModel):
    card_id: int
    word_pair_id: int
    estonian: str
    finnish: str
    direction: str
    category: str


class ReviewRequest(BaseModel):
    card_id: int
    quality: int  # 0-5 SM-2 quality


class ReviewResponse(BaseModel):
    next_review: str
    interval: int
    ease_factor: float
    repetitions: int
    xp_earned: int


@router.get("/due", response_model=list[DueCardResponse])
async def get_due_cards(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    result = await db.execute(
        select(SRSCard, WordPair)
        .join(WordPair, SRSCard.word_pair_id == WordPair.id)
        .where(and_(SRSCard.user_id == user.id, SRSCard.next_review <= now))
        .order_by(SRSCard.next_review)
        .limit(limit)
    )
    cards = result.all()
    return [
        DueCardResponse(
            card_id=card.id,
            word_pair_id=pair.id,
            estonian=pair.estonian,
            finnish=pair.finnish,
            direction=card.direction,
            category=pair.category,
        )
        for card, pair in cards
    ]


@router.post("/review", response_model=ReviewResponse)
async def submit_review(
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SRSCard).where(
            and_(SRSCard.id == req.card_id, SRSCard.user_id == user.id)
        )
    )
    card = result.scalar_one_or_none()
    if not card:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Card not found")

    # SM-2 calculation
    card.ease_factor, card.interval, card.repetitions = calculate_sm2(
        quality=req.quality,
        ease_factor=card.ease_factor,
        interval=card.interval,
        repetitions=card.repetitions,
    )
    card.last_reviewed = datetime.utcnow()
    card.next_review = datetime.utcnow() + __import__("datetime").timedelta(days=card.interval)

    # XP
    xp = 10 if req.quality >= 3 else 5

    # Update progress
    prog_result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    progress = prog_result.scalar_one_or_none()
    if not progress:
        progress = UserProgress(user_id=user.id)
        db.add(progress)
        await db.flush()  # Get default values from DB

    progress.total_reviews = (progress.total_reviews or 0) + 1
    if req.quality >= 3:
        progress.correct_reviews = (progress.correct_reviews or 0) + 1
    progress.xp = (progress.xp or 0) + xp
    progress.level = 1 + progress.xp // 100
    progress.last_activity = datetime.utcnow()

    await db.flush()

    return ReviewResponse(
        next_review=card.next_review.isoformat(),
        interval=card.interval,
        ease_factor=round(card.ease_factor, 2),
        repetitions=card.repetitions,
        xp_earned=xp,
    )


@router.post("/init")
async def init_srs_cards(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create SRS cards for all word pairs (first-time setup)."""
    result = await db.execute(select(WordPair.id))
    pair_ids = result.scalars().all()

    created = 0
    for pid in pair_ids:
        for direction in ("et_fi", "fi_et"):
            existing = await db.execute(
                select(SRSCard).where(
                    and_(
                        SRSCard.user_id == user.id,
                        SRSCard.word_pair_id == pid,
                        SRSCard.direction == direction,
                    )
                )
            )
            if not existing.scalar_one_or_none():
                card = SRSCard(user_id=user.id, word_pair_id=pid, direction=direction)
                db.add(card)
                created += 1

    await db.flush()
    return {"created": created}
