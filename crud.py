from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas

# --- basic crud stuff ---

def create_student(db: Session, student: schemas.StudentCreate):
    new_student = models.Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def update_student(db: Session, student_id: int, updates: schemas.StudentUpdate):
    student = get_student(db, student_id)
    if not student:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student

def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True

# --- these ones are for the chatbot, just simple aggregate queries ---

def count_students(db: Session):
    return db.query(func.count(models.Student.id)).scalar()

def count_students_by_gender(db: Session, gender: str):
    return db.query(func.count(models.Student.id)).filter(
        func.lower(models.Student.gender) == gender.lower()
    ).scalar()

def average_grade(db: Session):
    return db.query(func.avg(models.Student.grade)).scalar()

def students_by_course(db: Session, course: str):
    return db.query(models.Student).filter(
        func.lower(models.Student.course) == course.lower()
    ).all()
