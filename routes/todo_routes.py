from fastapi import APIRouter, Depends, HTTPException
from controllers.todo_controller import TodoController
from models.todo import TodoCreate, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["todos"])

@router.get("/")
async def get_all_todos():
    controller = TodoController()
    return await controller.get_all_todos()

@router.get("/{todo_id}")
async def get_todo_by_id(todo_id: int):
    controller = TodoController()
    result = await controller.get_todo_by_id(todo_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.post("/")
async def create_todo(todo: TodoCreate):
    controller = TodoController()
    result = await controller.create_todo(todo)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.put("/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    controller = TodoController()
    result = await controller.update_todo(todo_id, todo)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int):
    controller = TodoController()
    result = await controller.delete_todo(todo_id)
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result