from config.supabase import supabase
from models.todo import Todo, TodoCreate, TodoUpdate
from views.todo_view import TodoView

class TodoController:
    async def get_all_todos(self):
        response = supabase.table("todos").select("*").execute()
        todos = [dict(todo) for todo in response.data]
        return TodoView.render_todos(todos)

    async def get_todo_by_id(self, todo_id: int):
        response =  supabase.table("todos").select("*").eq("id", todo_id).execute()
        todo = response.data[0] if response.data else None
        return TodoView.render_todo(todo)

    async def create_todo(self, todo: TodoCreate):
        response =  supabase.table("todos").insert({
            "task": todo.task,
            "completed": False
        }).execute()
        return TodoView.render_todo(response.data[0])

    async def update_todo(self, todo_id: int, todo: TodoUpdate):
        updates = {}
        if todo.task is not None:
            updates["task"] = todo.task
        if todo.completed is not None:
            updates["completed"] = todo.completed
        response =  supabase.table("todos").update(updates).eq("id", todo_id).execute()
        todo = response.data[0] if response.data else None
        return TodoView.render_todo(todo)

    async def delete_todo(self, todo_id: int):
        response =  supabase.table("todos").delete().eq("id", todo_id).execute()
        if not response.data:
            return TodoView.render_error("Todo not found")
        return TodoView.render_success("Todo deleted")