from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import CheckConstraint
from wtforms import SelectMultipleField
from werkzeug.security import generate_password_hash, check_password_hash


from datetime import datetime
import pytz


#flask --app app run   use this to run app
# http://127.0.0.1:5000/ # link to webaddress

app = Flask(__name__, static_url_path='/static')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SECRET_KEY"] = "mysecret"
db = SQLAlchemy(app)
admin = Admin(app)

app.app_context().push() # without this, I recieve flask error


# databases

class AdminLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)\

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    inbox = db.relationship('Message', back_populates='sender', primaryjoin="User.id==Message.sender_id")
    sent = db.relationship('Message', back_populates='recipient', primaryjoin="User.id==Message.recipient_id")
    def __repr__(self):
        return self.email

    @property
    def is_active(self):
        # For simplicity, always consider the teacher account as active
        return True

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender = db.relationship('User', back_populates='inbox', primaryjoin="User.id==Message.sender_id")
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.relationship('User', back_populates='sent', primaryjoin="User.id==Message.recipient_id")

class UserView(ModelView):
    form_columns = ["email", "password"]
    column_list = ["id", "email", "password", "inbox", "sent"]

    #form_args = {
    #    'body': {
    #}

class AdminLoginView(ModelView):
    pass

class EventView(ModelView):
    form_columns = ["date", "time", "event", "user"]
    column_list = ["date", "time", "event", "user"]

    #form_args = {
    #    'body': {
    #}

class MessageView(ModelView):
    form_columns = ["body", "timestamp", "sender", "recipient"]
    column_list = ["body", "timestamp", "sender", "recipient"]

    #form_args = {
    #    'body': {
    #}
 

admin.add_view(UserView(User, db.session))
admin.add_view(EventView(Event, db.session))
admin.add_view(MessageView(Message, db.session))
admin.add_view(AdminLoginView(AdminLogin, db.session))

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

# Function to register a new user // can only register new students or teachers
@app.route('/register_backend', methods=['POST'])
def register_backend():

    name = request.form.get('new_name')
    email = request.form.get('new_email')
    password = request.form.get('new_password')

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        flash('Email address already exists:')
        return redirect(url_for("register"))
        #return jsonify({"error": "User with this email already exists"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    # new_user = User(email=email, password=hashed_password)

    new_user = User(name = name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    flash('Account created successfully!')
    return render_template('login.html')


@app.route("/login_backend", methods=["POST"])
def login_backend():

    Email = request.form['email']
    Password = request.form['password']

    user = User.query.filter_by(email=Email).first()

    # Check if the email ends with "@type" and assign role at login
    if user is not None:
        if not user.password.startswith('$pbkdf2'):

            if (user.password == Password):
                print("passed commited!")
                hashed_password = generate_password_hash(Password, method='pbkdf2:sha256')
                user.password = hashed_password
                db.session.commit()

        if check_password_hash(user.password, Password):

            session['id'] = user.id

            return redirect(url_for('dashboard', id = user.id))

        else:
            flash('Password is incorrect: try again')
            return redirect(url_for("login"))
            #return jsonify({"error": "Password is not correct"}), 404
    else:
        flash('Email not found or invalid login credentials')
        return redirect(url_for("login"))
        #return jsonify({"error": "Invalid request: Email not found or invalid login credentials"}), 404


@app.route('/dashboard/<id>')
def dashboard(id):
    return render_template('dashboard.html', user_id=id)

@app.route('/dashboard/calendar/<id>')
def calendar(id):
    return render_template('calendar.html', user_id=id)

@app.route('/dashboard/eventform/<id>')
def eventform(id):
    return render_template('event_form.html', user_id=id)

@app.route('/dashboard/messages/<id>')
def messages(id):
    user = User.query.get(id)
    sent_messages = Message.query.filter_by(sender_id=id).all()
    received_messages = Message.query.filter_by(recipient_id=id).all()
    if user:
        return render_template('messages.html', user_id=user.id , user_email=user.email, received_messages=received_messages, sent_messages=sent_messages, users=User.query.all())
    return "User not found."


@app.route('/eventform_backend/<id>', methods=['POST'])
def eventform_backend(id):

    user = User.query.filter_by(id=id).first()

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_time = request.form['event_time']


        # Create and add the event to the database
        new_event = Event(date=event_date, time=event_time, event=event_name, user=user)
        db.session.add(new_event)
        db.session.commit()

        flash('Event created successfully!')
        return redirect(url_for('dashboard', id=id))

    return render_template('event_form.html', user_id=id)


@app.route('/get_events/<user_id>')
def get_events(user_id):
    events = Event.query.filter_by(user_id=user_id).all()
    event_list = []

    for event in events:

        start_datetime_str = f'{event.date}T{event.time}'

        event_list.append({
            'title': event.event,
            'start': start_datetime_str ,
            'end': '',
            'url': '',   #work on this! this is how its inputed into the calender. you can add more stuff
            'color': 'blue',  # Set a specific color for the event
            'description': 'Some additional information about the event',
            # 'editable': True,  # Make the event non-editable
            # 'extendedProps': {
            #     'hours': '08',  # Include additional custom properties
            #     'minutes': '30',
            # }
        })

    return jsonify(event_list)


# Routes for sending and viewing messages
@app.route('/dashboard/messages/<id>/send_message', methods=['GET', 'POST'])
def send_message(id):
    email = request.form.get('email')
    user = User.query.get(id)
    body = request.form.get('body')

    existing_user = User.query.filter_by(email=email).first()

    if existing_user is None:
        flash('Email address does not exist in our database')
        return redirect(url_for("messages", id=user.id))

    new_msg = Message(body=body, sender_id=id, recipient_id=existing_user.id)

    db.session.add(new_msg)
    db.session.commit()

    sent_messages = Message.query.filter_by(sender_id=id).all()
    received_messages = Message.query.filter_by(recipient_id=id).all()
    return render_template('messages.html', user_id=id, user_email=user.email, received_messages=received_messages, sent_messages=sent_messages, users=User.query.all())

@app.route('/timezone/<time>')
def timezone(time):

    # Get user's timezone from request or user preferences
    user_timezone = request.args.get('timezone', 'UTC')

    # Get current time in UTC
    utc_now = datetime.utcnow()

    # Convert UTC time to user's timezone
    user_timezone_obj = pytz.timezone(user_timezone)
    local_time = utc_now.replace(tzinfo=pytz.utc).astimezone(user_timezone_obj)

    # Print user's timezone to console
    print(f"User's timezone: {user_timezone}")

    return f"Local time in {user_timezone}: ------- {local_time}"



if __name__ == '__main__':
    # with app.app_context():
    #     db.drop_all()
    #     # Create tables
    #     db.create_all()

        # Create a user
        # new_user = User(email='john@example.com', password='password123')
        # test = User(email='test@example.com', password='abc123')
        # test2 = User(email='test2@example.com', password='abc123')
        # db.session.add(new_user)
        # db.session.add(test)
        # db.session.add(test2)
        # db.session.commit()

        # Add events for the user
        # event1 = Event(date='2023-12-25', time='10:00 AM', event='Christmas celebration', user=new_user)
        # event2 = Event(date='2023-11-30', time='3:00 PM', event='Meeting with John', user=new_user)
        # db.session.add(event1)
        # db.session.add(event2)
        # db.session.commit()

        # Add messages for the user
        #msg1 = Message(content='Hello, how are you?', time='10:00 AM', sender_id=new_user.id, receiver_id=test.id)
        #db.session.add(msg1)
        #db.session.commit()

        # Retrieve all events for a specific user (e.g., the user with ID=1)
        # user_id = 1  # Assuming the user ID is 1 for the newly created user
        # user_events = Event.query.filter_by(user_id=user_id).all()
        # for event in user_events:
        #     print(event)

        # Retrieve a specific user and their associated events
        # user = User.query.filter_by(id=user_id).first()
        # print(f"User Email: {user.email}, User Password: {user.password}")
        # print("User's Events:")
        # for eventt in user.events:
        #     print(f"Date: {eventt.date}, Time: {eventt.time}, Event= {eventt.event}")

        # Retrieve messages for the user
        #user_messages_received = Message.query.filter_by(receiver_id=user.id).all()
        #user_messages_sent = Message.query.filter_by(sender_id=user.id).all()
        #print("User's Messages:")
        #if user_messages_sent:
        #    print(f"Sender: {user.email}")
        #    for sent_message in user_messages_sent:
        #        print(f"Message Content: {sent_message.content}, Time: {sent_message.time}")
        #        print(f"Receiver: {sent_message.receiver.email}")

    db.drop_all()
    db.create_all()
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
