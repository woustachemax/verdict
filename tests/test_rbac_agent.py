from src.agent.rbac_agent import evaluate_access


def test_admin_can_delete():
    result = evaluate_access(role="admin", action="delete", resource="audit")
    assert result["allowed"] is True
    assert result["decision"] == "allow"


def test_viewer_cannot_delete():
    result = evaluate_access(role="viewer", action="delete", resource="audit")
    assert result["allowed"] is False
    assert result["decision"] == "deny"
