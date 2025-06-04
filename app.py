from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for flash messages

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'musiimentatendodivine@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD', 'Purpose@1')

db = SQLAlchemy(app)
mail = Mail(app)
scheduler = BackgroundScheduler()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120))
    last_reminder = db.Column(db.DateTime)

    def __repr__(self):
        return '<Task %r>' % self.id

def send_reminder_email(task_id):
    with app.app_context():
        task = Todo.query.get(task_id)
        if task and not task.complete and task.email:
            msg = Message('Task Reminder',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[task.email])
            msg.body = f'Reminder: You have a pending task - {task.content}'
            try:
                mail.send(msg)
                task.last_reminder = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

def schedule_reminders(task_id):
    scheduler.add_job(
        func=send_reminder_email,
        trigger='interval',
        hours=6,
        args=[task_id],
        id=f'task_{task_id}'
    )

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_email = request.form['email']
        new_task = Todo(content=task_content, email=task_email)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            schedule_reminders(new_task.id)
            flash('Task added successfully!')
            return redirect('/')
        except Exception as e:
            return f'There was an issue adding your task: {str(e)}'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        # Remove the scheduled job if it exists
        try:
            scheduler.remove_job(f'task_{id}')
        except:
            pass
        
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.email = request.form['email']
        
        try:
            db.session.commit()
            # Reschedule reminder if email changed
            try:
                scheduler.remove_job(f'task_{id}')
            except:
                pass
            if task.email:
                schedule_reminders(task.id)
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)

@app.route('/complete/<int:id>')
def complete(id):
    task = Todo.query.get_or_404(id)
    try:
        task.complete = not task.complete
        db.session.commit()
        
        # Remove reminder if task is completed
        if task.complete:
            try:
                scheduler.remove_job(f'task_{id}')
            except:
                pass
        else:
            # Reschedule if task is marked as incomplete
            if task.email:
                schedule_reminders(task.id)
                
        return redirect('/')
    except:
        return 'There was an issue updating the task status'

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True) 
