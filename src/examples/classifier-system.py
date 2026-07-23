def classify_message(message: str) -> str:
    normalized = message.strip().lower()
    emotional_markers = {"feel", "sad", "angry", "hurt", "afraid", "upset", "worried"}
    logical_markers = {"how", "what", "why", "when", "recommend", "should", "compare"}
    if any(token in normalized for token in emotional_markers):
        return "emotional"
    if any(token in normalized for token in logical_markers):
        return "logical"
    return "logical"


def generate_response(message: str) -> str:
    category = classify_message(message)
    if category == "emotional":
        return "I hear you. That sounds difficult, and it is okay to take time to sort through it."
    return "Here is a clear answer: focus on the main issue, weigh the key trade-offs, and choose the option that meets your core need."


if __name__ == "__main__":
    print(generate_response(input("Enter a message: ")) )
