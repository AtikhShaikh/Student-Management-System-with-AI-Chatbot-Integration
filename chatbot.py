# chatbot.py
# handles the AI chatbot part - takes a question, figures out what the user
# wants using gemini, pulls the data from the db, then gets gemini to write
# a normal english answer back

import os
import json
from typing import TypedDict, Optional

from google import genai
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

import crud

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_client = None

def get_client():
    global _client
    if _client is None:
        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY not set, add it to .env")
        _client = genai.Client(api_key=key)
    return _client


class ChatState(TypedDict):
    question: str
    intent: Optional[str]
    param: Optional[str]
    data: Optional[str]
    answer: Optional[str]


INTENTS = ["count_all", "count_by_gender", "average_grade", "students_by_course", "unknown"]


# step 1 - figure out what the user is actually asking
def classify_intent(state: ChatState) -> ChatState:
    client = get_client()

    prompt = f"""Look at the question below and turn it into JSON with "intent" and "param".

Possible intents: {INTENTS}
- count_by_gender -> param is the gender they asked about
- students_by_course -> param is the course name
- count_all / average_grade -> param is null
- if nothing matches, use unknown

Only return the JSON, nothing else.

Question: {state['question']}"""

    res = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw = res.text.strip().strip("`").replace("json\n", "").strip()

    try:
        parsed = json.loads(raw)
        state["intent"] = parsed.get("intent", "unknown")
        state["param"] = parsed.get("param")
    except json.JSONDecodeError:
        # gemini didn't give clean json, just fall back
        state["intent"] = "unknown"
        state["param"] = None

    return state


# step 2 - go get the actual data based on the intent
def make_retrieve_data(db: Session):
    def retrieve_data(state: ChatState) -> ChatState:
        intent = state.get("intent")

        if intent == "count_all":
            state["data"] = json.dumps({"total_students": crud.count_students(db)})

        elif intent == "count_by_gender":
            gender = state.get("param") or ""
            state["data"] = json.dumps({"gender": gender, "count": crud.count_students_by_gender(db, gender)})

        elif intent == "average_grade":
            state["data"] = json.dumps({"average_grade": crud.average_grade(db)})

        elif intent == "students_by_course":
            course = state.get("param") or ""
            students = crud.students_by_course(db, course)
            state["data"] = json.dumps({
                "course": course,
                "students": [{"id": s.id, "name": s.name, "grade": s.grade} for s in students]
            })

        else:
            state["data"] = json.dumps({"error": "couldn't figure out what you're asking"})

        return state

    return retrieve_data


# step 3 - turn the raw data into a normal sentence
def generate_answer(state: ChatState) -> ChatState:
    client = get_client()

    prompt = f"""The user asked: "{state['question']}"

Data from the database: {state.get('data')}

Write a short answer using only this data, don't make up numbers."""

    res = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    state["answer"] = res.text.strip()
    return state


def build_graph(db: Session):
    graph = StateGraph(ChatState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_data", make_retrieve_data(db))
    graph.add_node("generate_answer", generate_answer)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "retrieve_data")
    graph.add_edge("retrieve_data", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


def ask_chatbot(db: Session, question: str) -> str:
    app = build_graph(db)
    result = app.invoke({"question": question, "intent": None, "param": None, "data": None, "answer": None})
    return result["answer"]
