import os
from typing import Any

from src.agent.observability import trace_agent_call
from src.config import settings

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - exercised when optional dependency is missing
    ChatPromptTemplate = None
    StrOutputParser = None
    ChatOpenAI = None


if settings.ENV == "production" and not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY must be set in production")


def _build_model():
    if ChatOpenAI is None:
        return None
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


if ChatPromptTemplate is not None:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an RBAC policy evaluator. Return JSON with allowed, decision, reason, role, action, resource.",
            ),
            (
                "human",
                "Evaluate whether {role} can perform {action} on {resource}. Use allow only when the role has explicit permission."
            ),
        ]
    )
else:
    prompt = None


def evaluate_access(role: str, action: str, resource: str) -> dict[str, Any]:
    if role == "admin":
        return {"allowed": True, "decision": "allow", "reason": "Admins have broad permissions", "role": role, "action": action, "resource": resource}

    if role == "viewer" and action in {"read"}:
        return {"allowed": True, "decision": "allow", "reason": "Viewers can read", "role": role, "action": action, "resource": resource}

    return {"allowed": False, "decision": "deny", "reason": "Role lacks permission", "role": role, "action": action, "resource": resource}


def evaluate_with_langchain(role: str, action: str, resource: str) -> dict[str, Any]:
    result = evaluate_access(role=role, action=action, resource=resource)
    if os.getenv("OPENAI_API_KEY") and prompt is not None and _build_model() is not None and StrOutputParser is not None:
        try:
            chain = prompt | _build_model() | StrOutputParser()
            response = chain.invoke({"role": role, "action": action, "resource": resource})
            result["reason"] = response
            result["decision"] = "allow" if result["allowed"] else "deny"
        except Exception:
            pass

    trace_agent_call("rbac-evaluation", {"role": role, "action": action, "resource": resource}, result)
    return result
