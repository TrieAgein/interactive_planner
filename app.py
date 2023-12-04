from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import CheckConstraint


#flask --app app run   use this to run app
# http://127.0.0.1:5000/ # link to webaddress

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SECRET_KEY"] = "mysecret"
db = SQLAlchemy(app)
admin = Admin(app)

app.app_context().push() # without this, I recieve flask error


# databases
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Event, db.session))

@app.route('/')
def launch():
 return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/run')
def run():
    return "<p>Is indeed running page</p>"

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        # Create tables
        db.create_all()

        # Create a user
        new_user = User(email='john@example.com', password='password123')
        db.session.add(new_user)
        db.session.commit()

        # Add events for the user
        event1 = Event(date='2023-12-25', time='10:00 AM', event='Christmas celebration', user=new_user)
        event2 = Event(date='2023-11-30', time='3:00 PM', event='Meeting with John', user=new_user)
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()

        # Retrieve all events for a specific user (e.g., the user with ID=1)
        user_id = 1  # Assuming the user ID is 1 for the newly created user
        user_events = Event.query.filter_by(user_id=user_id).all()
        for event in user_events:
            print(event)

        # Retrieve a specific user and their associated events
        user = User.query.filter_by(id=user_id).first()
        print(f"User Email: {user.email}, User Password: {user.password}")
        print("User's Events:")
        for eventt in user.events:
            print(f"Date: {eventt.date}, Time: {eventt.time}, Event= {eventt.event}")

    app.run(debug=True)

# Notes 

#install//

# pip install blinker==1.6.2 click==8.1.6 Flask==2.3.2 Flask-Admin==1.6.1 Flask-SQLAlchemy==3.0.5 greenlet==2.0.2 itsdangerous==2.1.2 Jinja2==3.1.2 MarkupSafe==2.1.3 SQLAlchemy==2.0.19 typing_extensions==4.7.1 Werkzeug==2.3.6 WTForms==3.0.1 flask_login==23.2.1
# pip install flask-bcrypt
# pip install pytz


### how to delete or create db. type into terminal
#  flask shell
# >>>
# >>> from app import db
# >>> db.drop_all()
# >>> db.create_all()
# >>> exit()

# flask --app app run   use this to run app


### how to add in to database using terminal.
#>>> from app import app      use this to avoid error
#>>> from app import db
#>>> from app import User
#>>> user1 = User(studentName="student1",email="somethin@gmail" ,password="something",role="student")
#>>> db.session.add(user1)
#>>> db.session.commit()
#>>> user1 = User(studentName="student1",email="somethin@gmail" ,password="something",role="student")
#>>> db.session.add(user1)
#>>> db.session.commit()
