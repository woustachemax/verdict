import os
from typing import Any

from langfuse import Langfuse

from src.config import settings


langfuse = None
if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
    langfuse = Langfuse(
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
    )


def trace_agent_call(name: str, input_data: dict[str, Any], output_data: dict[str, Any]) -> None:
    if langfuse is None:
        return
    try:
        langfuse.trace(
            name=name,
            input=input_data,
            output=output_data,
            metadata={"environment": settings.ENV},
        )
    except Exception:
        return
