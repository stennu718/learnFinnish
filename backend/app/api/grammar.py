"""Grammar API routes — Estonian-Finnish case transformation exercises."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.models import User
from app.services.grammar import (
    get_all_rules, get_rule_by_name, generate_exercise,
    generate_all_exercises, apply_rule,
)

router = APIRouter()


class CaseRuleResponse(BaseModel):
    name: str
    estonian_ending: str
    finnish_ending: str
    description: str
    examples: list[dict]


class ExerciseResponse(BaseModel):
    rule_name: str
    description: str
    estonian: str
    finnish: str
    estonian_sentence: str
    finnish_sentence: str


class ApplyRuleRequest(BaseModel):
    word: str = Field(..., min_length=1, max_length=200)
    rule_name: str = Field(..., min_length=1, max_length=100)


class ApplyRuleResponse(BaseModel):
    original: str
    transformed: str
    rule_name: str
    description: str


@router.get("/rules", response_model=list[CaseRuleResponse])
async def list_rules(user: User = Depends(get_current_user)):
    rules = get_all_rules()
    return [CaseRuleResponse(
        name=r.name,
        estonian_ending=r.estonian_ending,
        finnish_ending=r.finnish_ending,
        description=r.description,
        examples=r.examples
    ) for r in rules]


@router.get("/rules/{rule_name}", response_model=CaseRuleResponse)
async def get_rule(rule_name: str, user: User = Depends(get_current_user)):
    rule = get_rule_by_name(rule_name)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return CaseRuleResponse(
        name=rule.name,
        estonian_ending=rule.estonian_ending,
        finnish_ending=rule.finnish_ending,
        description=rule.description,
        examples=rule.examples
    )


@router.get("/exercises", response_model=list[ExerciseResponse])
async def list_exercises(user: User = Depends(get_current_user)):
    exercises = generate_all_exercises()
    return [ExerciseResponse(**e) for e in exercises]


@router.get("/exercises/{rule_name}", response_model=ExerciseResponse)
async def get_exercise(rule_name: str, user: User = Depends(get_current_user)):
    rule = get_rule_by_name(rule_name)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    exercise = generate_exercise(rule)
    return ExerciseResponse(**exercise)


@router.post("/apply", response_model=ApplyRuleResponse)
async def apply_case_rule(req: ApplyRuleRequest, user: User = Depends(get_current_user)):
    rule = get_rule_by_name(req.rule_name)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    transformed = apply_rule(req.word, rule)
    return ApplyRuleResponse(
        original=req.word,
        transformed=transformed,
        rule_name=rule.name,
        description=rule.description
    )
