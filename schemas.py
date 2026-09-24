from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class StudentBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    course: Optional[str] = None
    grade: Optional[float] = None
    email: Optional[EmailStr] = None

class StudentCreate(StudentBase):
    pass

# update schema - everything optional so you can send just the fields you wanna change
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    course: Optional[str] = None
    grade: Optional[float] = None
    email: Optional[EmailStr] = None

class StudentOut(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
