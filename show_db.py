from app import app, db, Todo

with app.app_context():
    # Get all todos
    todos = Todo.query.all()

    print("\nDatabase Contents:")
    print("-----------------")
    if todos:
        for todo in todos:
            print(f"ID: {todo.id}")
            print(f"Content: {todo.content}")
            print(f"Completed: {todo.complete}")
            print(f"Date Created: {todo.date_created}")
            print("-----------------")
    else:
        print("No tasks found in the database.") 