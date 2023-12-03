from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy


#flask --app app run   use this to run app
# http://127.0.0.1:5000/ # link to webaddress

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
app.config["SECRET_KEY"] = "mysecret"
db = SQLAlchemy(app)


app.app_context().push() # without this, I recieve flask error


# databases





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
