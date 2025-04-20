import json
from pathlib import Path
from uuid import UUID
from typing import Annotated

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
import pandas as pd


app = FastAPI()


DATA = json.loads(Path("data.json").read_text(encoding="utf-8"))
HTML = Path("test.html").read_text(encoding="utf-8")


DATABASE_FILE: Path = Path(__file__).parent / "db" / "quizulon.db"
DATABASE_URL: str = f"sqlite:///{DATABASE_FILE}"

CONNECT_ARGS = { "check_same_thread": False }

ENGINE = create_engine(DATABASE_URL, echo=True, connect_args=CONNECT_ARGS)
SQLModel.metadata.create_all(ENGINE)

class ChoiceBase(SQLModel):
    """A response option for a question"""
    text: str = Field(index=False)
    correct: bool | None = Field(index=True)

class Choice(ChoiceBase, table=True):
    """A response option for a question, suitable for a database"""
    id: int | None = Field(default=None, primary_key=True)

    question_id: int | None = Field(default=None, foreign_key="question.id")

class QuestionBase(SQLModel):
    """Elements included in every question"""
    text: str
    choices: list[Choice]

class Question(QuestionBase, table=True):
    """Database-aware version of question"""
    id: int

class Learner(SQLModel):
    """Someone taking the quiz"""
    id: UUID
    name: str

@app.get("/ws/html/")
async def root() -> HTMLResponse:
    """Default webpage"""
    return HTMLResponse(HTML)


class ConnectionManager:
    """Handle a pool of websocket connections"""
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Actions for when a client connects"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Actions for when a client disconnects"""
        self.active_connections.remove(websocket)

    async def send_individual_message(self, message: str, websocket: WebSocket) -> None:
        """Send a message to a single client"""
        await websocket.send_json(data=message)

    async def broadcast(self, message: str) -> None:
        """Send a message to all clients"""
        for connection in self.active_connections:
            await connection.send_json(data=message)


manager = ConnectionManager()


def grade_question(question, response):
    for choice in question.get("choices"):
        if choice.get("correct"):
            return choice.get("id") == response.get("answer_id")


def get_learner_name(learner_id):
    learners = DATA.get("learners")
    for learner in learners:
        if learner.get("learner_id") == learner_id:
            return learner.get("learner_name")


def get_grades():
    questions = DATA.get("questions")
    correct_responses = {}
    for question in questions:
        for choice in question.get("choices"):
            if choice.get("correct"):
                correct_responses[question["id"]] = choice["id"]
    learner_names = []
    learner_guesses = []
    question_ids = []
    corrects = []
    for response in DATA["responses"]:
        learner_names.append(get_learner_name(response["learner_id"]))
        learner_guesses.append(response["answer_id"])
        qid = response["question_id"]
        question_ids.append(qid)
        corrects.append(correct_responses[qid])
    df = pd.DataFrame(
        {
            "question": question_ids,
            "learner": learner_names,
            "response": learner_guesses,
            "answer": corrects,
        }
    )
    return df.to_dict()


@app.websocket("/ws/proctor/")
async def proctor_socket(websocket: WebSocket):
    await websocket.accept()
    while True:
        msg = await websocket.receive_json()
        await websocket.send_json(process_proctor_message(msg))


def process_proctor_message(msg):
    match msg.get("message_type"):
        case "Question":
            new_question_id = msg.get("id")
            questions = DATA.get("questions")
            q = [
                qi for qi in filter(lambda q: q.get("id") == new_question_id, questions)
            ]
            manager.broadcast(q[0].get("choices"))
            return {q[0]}
        case "Response":
            DATA["responses"].append(
                {
                    "question_id": msg.get("question_id"),
                    "answer_id": msg.get("answer_id"),
                    "learner_id": msg.get("learner_id"),
                    "message_type": "Response"
                }
            )
            return DATA
        case "Learner":
            DATA["learners"].append(
                {
                    "learner_id": msg.get("learner_id"),
                    "learner_name": msg.get("learner_name"),
                    "message_type": "Learner"
                }
            )
            return DATA
        case "Results":
            return get_grades()


@app.websocket("/ws/learner/{client_id}")
async def learner_socket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            process_proctor_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
