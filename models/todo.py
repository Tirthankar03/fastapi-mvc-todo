from pydantic import BaseModel

class TodoBase(BaseModel):
    task: str

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    task: str | None = None
    completed: bool | None = None

class Todo(TodoBase):
    id: int
    completed: bool
    created_at: str

    class Config:
        orm_mode = True