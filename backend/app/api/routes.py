from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ...llm_orchestrator import run_agent
from ..core.config import get_settings
from ..models.schemas import QueryRequest, QueryResponse

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: Request,
    payload: QueryRequest,
) -> QueryResponse:
    try:
        await limiter(request)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded, please retry later.",
        ) from exc

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty")

    user_id = payload.user_id or "anonymous"
    try:
        result = await run_agent(question=question, user_id=user_id)
    except ValueError as exc:
        logger.exception("Invalid SQL generated: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to process query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process question"
        ) from exc

    return QueryResponse(**result)
