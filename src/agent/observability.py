import logging
from typing import Any

logger = logging.getLogger("agent")
logger.addHandler(logging.NullHandler())

def trace_agent_call(name: str, input_data: dict[str, Any], output_data: dict[str, Any]) -> None:
    logger.debug("agent call %s %s -> %s", name, input_data, output_data)
