from langchain.chat_models import init_chat_model
from langgraph.graph import START, END, StateGraph
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, Literal
from typing_extensions import TypedDict


load_dotenv()
llm = init_chat_model("anthropic:claude-haiku-4-5-20251001")


class State(TypedDict):
    messages:  Annotated[list, add_messages]
    message_type: str | None

class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message is emotional or logical response" 
    )

def Classify_Message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifier)
    res = classifier_llm.invoke([
        {
            "role": "system",
            "content": """You classify the user's message as either "emotional" or "logical".
            Classify as "emotional" if the message expresses feelings, seeks comfort or validation, describes a personal struggle, or is venting without asking for a solution.
            Classify as "logical" if the message asks for facts, analysis, a decision, a recommendation, or step-by-step reasoning, even if it touches on a personal situation.
            Return only the classification, nothing else."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ])
    return {"message_type": res.message_type}

def Router(state:State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next":"emotional"}
    return {"next": "logical"}


def Emotional_Agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are a supportive, empathetic assistant. The user's message has been classified as emotional.
            Respond with warmth and validation first, acknowledge what they're feeling before offering anything else. Don't rush to solve the problem or give advice unless they clearly ask for it. Keep your tone genuine and human, not clinical or robotic. Reflect back what you're hearing so they feel understood.
            Avoid being dismissive, avoid jumping straight to logic or fixes, and avoid generic platitudes."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [reply]}


def Logical_Agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {
            "role": "system",
            "content": """You are a clear, analytical assistant. The user's message has been classified as logical.
            Respond with facts, structured reasoning, or a direct recommendation. Get to the point, minimal padding, no unnecessary hedging. If there are trade-offs, lay them out briefly rather than avoiding a stance.
            Avoid excessive emotional language or validation that isn't needed here, focus on being useful and precise."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [reply]}


graph_builder = StateGraph(State)
graph_builder.add_node("classifier", Classify_Message)
graph_builder.add_node("router", Router)
graph_builder.add_node("emotional", Emotional_Agent)
graph_builder.add_node("logical", Logical_Agent)


graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges("router",
                        lambda state:state.get("next"),
                        {"emotional": "emotional", "logical":"logical"})

graph_builder.add_edge("emotional", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()


def run_chatbot():
    state = {"messages": [], "message_type": None}

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Bye")
            break

        state["messages"] = state["messages"] + [{"role": "user", "content": user_input}]
        state = graph.invoke(state)

        last_message = state["messages"][-1]
        print(f"Assistant: {last_message.content}")


if __name__ == "__main__":
    run_chatbot()