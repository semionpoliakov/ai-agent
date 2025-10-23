"""Routes for the analytics query endpoint."""

import logging

from fastapi import APIRouter, Body, Depends, Request, status

from ...domain.models import QueryRequest, QueryResponse
from ...domain.services.orchestrator import QueryOrchestrator
from ...infra.config import get_settings
from ..deps import get_orchestrator_dep
from . import limiter

logger = logging.getLogger(__name__)

RATE_LIMIT = f"{get_settings().rate_limit_per_minute}/minute"

router = APIRouter()


@router.post("", response_model=QueryResponse, status_code=status.HTTP_200_OK)
@limiter.limit(RATE_LIMIT)
async def query_endpoint(
    request: Request,
    payload: QueryRequest = Body(...),
    orchestrator: QueryOrchestrator = Depends(get_orchestrator_dep),
) -> QueryResponse:
    try:
        result = await orchestrator.run(question=payload.question, user_id=payload.user_id)
    except ValueError:
        logger.exception("Invalid SQL generated for question=%s", payload.question[:80])
        raise
    except Exception:
        logger.exception("Failed to process query, returning stub response")
        return QueryResponse(
            sql="-- stubbed response while dependencies are unavailable",
            data=[],
            summary="Service is temporarily unavailable; showing placeholder data.",
        )
    return QueryResponse(**result)
