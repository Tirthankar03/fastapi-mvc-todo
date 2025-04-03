class TodoView:
    @staticmethod
    def render_todos(todos):
        return {"status": "success", "data": todos}

    @staticmethod
    def render_todo(todo):
        if not todo:
            return {"status": "error", "message": "Todo not found"}
        return {"status": "success", "data": todo}

    @staticmethod
    def render_error(message):
        return {"status": "error", "message": message}

    @staticmethod
    def render_success(message):
        return {"status": "success", "message": message}