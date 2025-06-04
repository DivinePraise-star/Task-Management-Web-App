from app import app, db, Todo

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    
    # Create new tables with updated schema
    db.create_all()
    
    # Add a sample task
    sample_task = Todo(
        content="Welcome to Task Master! This is a sample task.",
        email="example@example.com"
    )
    db.session.add(sample_task)
    db.session.commit()
    
    print("Database tables created successfully!")
    print("Added sample task to verify database works.") 