import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import pandas as pd


app = FastAPI()


DATA = json.loads(Path("data.json").read_text(encoding="utf-8"))
HTML = Path("test.html").read_text(encoding="utf-8")


@app.get("/ws/html/")
async def root():
    return HTMLResponse(HTML)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_individual_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


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
    return df.to_json()


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
            manager.broadcast(json.dumps(q[0].get("choices")))
            return json.dumps(q[0])
        case "Response":
            DATA["responses"].append(
                {
                    "question_id": msg.get("question_id"),
                    "answer_id": msg.get("answer_id"),
                    "learner_id": msg.get("learner_id"),
                }
            )
            return json.dumps(DATA)
        case "Learner":
            DATA["learners"].append(
                {
                    "learner_id": msg.get("learner_id"),
                    "learner_name": msg.get("learner_name"),
                }
            )
            return json.dumps(DATA)
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
