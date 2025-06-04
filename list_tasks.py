from app import app, Todo

def list_tasks():
    with app.app_context():
        tasks = Todo.query.all()
        
        print("\nCurrent Tasks in Database:")
        print("-------------------------")
        
        if tasks:
            for task in tasks:
                print(f"ID: {task.id}")
                print(f"Content: {task.content}")
                print(f"Completed: {task.complete}")
                print(f"Created: {task.date_created}")
                print("-------------------------")
        else:
            print("No tasks found in database.")

if __name__ == "__main__":
    list_tasks() 