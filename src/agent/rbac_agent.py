import json
import os
import subprocess
from pathlib import Path
from typing import Any

from src.agent.observability import trace_agent_call

RUST_AGENT_MANIFEST = Path(__file__).resolve().parents[2] / "rust_agent" / "Cargo.toml"
RUST_AGENT_RELEASE_BINARY = Path(__file__).resolve().parents[2] / "rust_agent" / "target" / "release" / "rust_agent"
RUST_AGENT_DEBUG_BINARY = Path(__file__).resolve().parents[2] / "rust_agent" / "target" / "debug" / "rust_agent"


def _normalize(value: str) -> str:
    return value.strip().lower()


def _local_access(role: str, action: str, resource: str) -> dict[str, Any]:
    score = 0.0
    if role == "admin":
        score += 4.0
    elif role == "viewer":
        score += 1.6
    else:
        score += 0.8
    score += {"read": 1.0, "write": 0.7, "delete": -0.2}.get(action, -0.5)
    score += 0.7 if "audit" in resource else 0.0
    score -= 0.4 if any(token in resource for token in ["secret", "config", "admin"]) else 0.0
    score += sum(0.2 for token in ["system", "user", "data", "settings"] if token in resource)
    score += min(len(resource) / 50.0, 0.5)
    allowed = score >= 1.5
    return {
        "allowed": allowed,
        "decision": "allow" if allowed else "deny",
        "reason": f"computed score {score:.2f} for role={role}, action={action}, resource={resource}",
        "role": role,
        "action": action,
        "resource": resource,
    }


def _build_rust_command(role: str, action: str, resource: str) -> list[str]:
    args = [role, action, resource]
    session_id = os.getenv("VERDICT_SESSION_ID")
    if session_id:
        args.extend(["--session-id", session_id])
    if RUST_AGENT_RELEASE_BINARY.exists():
        return [str(RUST_AGENT_RELEASE_BINARY), *args]
    if RUST_AGENT_DEBUG_BINARY.exists():
        return [str(RUST_AGENT_DEBUG_BINARY), *args]
    return [
        "cargo",
        "run",
        "--quiet",
        "--manifest-path",
        str(RUST_AGENT_MANIFEST),
        "--release",
        "--",
        *args,
    ]


def _rust_inference(role: str, action: str, resource: str) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            _build_rust_command(role, action, resource),
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(proc.stdout)
    except Exception:
        return _local_access(role, action, resource)


def evaluate_access(role: str, action: str, resource: str) -> dict[str, Any]:
    normalized_role = _normalize(role)
    normalized_action = _normalize(action)
    normalized_resource = _normalize(resource)
    return _local_access(normalized_role, normalized_action, normalized_resource)


def evaluate_with_rust(role: str, action: str, resource: str) -> dict[str, Any]:
    normalized_role = _normalize(role)
    normalized_action = _normalize(action)
    normalized_resource = _normalize(resource)
    result = _rust_inference(normalized_role, normalized_action, normalized_resource)
    trace_agent_call(
        "rbac-evaluation",
        {"role": normalized_role, "action": normalized_action, "resource": normalized_resource},
        result,
    )
    return result
