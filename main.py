from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
import crud
import chatbot
from database import engine, get_db

# create the tables if they don't already exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management System")


@app.get("/")
def root():
    return {"status": "ok", "message": "server is running"}


# ---- student crud routes ----

@app.post("/students/", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)


@app.get("/students/", response_model=list[schemas.StudentOut])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip, limit)


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    return student


@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, updates)
    if not student:
        raise HTTPException(status_code=404, detail="student not found")
    return student


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="student not found")
    return {"status": "deleted", "id": student_id}


# ---- chatbot route ----

@app.post("/chat/", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    try:
        answer = chatbot.ask_chatbot(db, request.question)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return schemas.ChatResponse(answer=answer)
