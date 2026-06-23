"""Word pairs API routes."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, WordPair

router = APIRouter()


class WordPairResponse(BaseModel):
    id: int
    estonian: str
    finnish: str
    estonian_example: str
    finnish_example: str
    category: str
    difficulty: int
    is_cognate: bool
    audio_url: str


@router.get("/", response_model=list[WordPairResponse])
@router.get("", response_model=list[WordPairResponse])
async def list_words(
    category: str | None = Query(None),
    cognates_only: bool = Query(False),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(WordPair)
    if category:
        query = query.where(WordPair.category == category)
    if cognates_only:
        query = query.where(WordPair.is_cognate == True)
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    pairs = result.scalars().all()
    return [WordPairResponse.model_validate(p.__dict__) for p in pairs]


@router.get("/categories")
@router.get("/categories/")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(WordPair.category).distinct())
    return result.scalars().all()
