from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import pytz
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)
application = app

nepal_tz = pytz.timezone('Asia/Kathmandu')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(nepal_tz))

# Get admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

@app.route('/')
def index():
    return render_template('index.html', year=datetime.now().year)

@app.route('/about')
def about():
    return render_template('about.html', year=datetime.now().year)

@app.route('/projects')
def projects():
    return render_template('projects.html', year=datetime.now().year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        new_message = Message(
            name=request.form.get('name'),
            email=request.form.get('email'),
            subject=request.form.get('subject'),
            message=request.form.get('message')
        )
        db.session.add(new_message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    messages = Message.query.order_by(Message.date.desc()).all()
    return render_template('admin_panel.html', messages=messages)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 