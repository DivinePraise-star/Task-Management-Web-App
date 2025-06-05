from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'your-secret-key-here'

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

@scheduler.scheduled_job('interval', hours=6)
def check_and_send_reminders():
    with app.app_context():
        tasks = Todo.query.filter_by(complete=False).all()
        for task in tasks:
            if task.email:
                if not task.last_reminder or datetime.utcnow() - task.last_reminder > timedelta(hours=6):
                    send_reminder_email(task.id)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        task_email = request.form['email']
        new_task = Todo(content=task_content, email=task_email)
        
        try:
            db.session.add(new_task)
            db.session.commit()
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
        return redirect('/')
    except:
        return 'There was an issue updating the task status'

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True) 
