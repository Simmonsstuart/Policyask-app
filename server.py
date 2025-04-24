# server.py

from fastapi import FastAPI
from pydantic import BaseModel
from policy_core import ask_question  # make sure this exists

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/ask")
def ask(query: Query):
    result = ask_question(query.question)
    return {"answer": result}
