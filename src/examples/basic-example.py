from src.agent.rbac_agent import evaluate_with_rust

if __name__ == "__main__":
    result = evaluate_with_rust("viewer", "read", "audit logs")
    print(result)
