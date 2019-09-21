import os
from time import localtime, strftime
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room, close_room

from wtform_fields import *
from dataModel import *

app = Flask(__name__)

#secret key - required for socketio - will be changed at deployment
app.config['SECRET_KEY'] = 'Replace later'

#db connect to postgress - changes at deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://eeuyotcvqfkbua:361187423674645ecc0637ec587f8b9d11b12767c50aecf338a298e7dde8e64d@ec2-174-129-18-42.compute-1.amazonaws.com:5432/d4daah96ejr9e0'

#db init
db = SQLAlchemy(app)

#socketio init
socketio = SocketIO(app)

#rooms used at chat
ROOMS = ["lounge", "student chat", "coding q & a", "general math"]

#creates and inits Login
login = LoginManager(app)
login.init_app(app)

#loads in user
@login.user_loader
def load_user(id):

    return User.query.get(int(id))

#main route login
@app.route('/', methods=['GET','POST'])
def login():

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)

#pulls up register page - currently student only
@app.route('/register', methods=['GET','POST'])
def new_student():

    #reg_forum from wtform_fields.py

    reg_form = RegistrationForm()
    # Updates database if validation is successful
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        firstname = reg_form.firstname.data
        lastname = reg_form.lastname.data
        email = reg_form.email.data
        password = reg_form.password.data

        # hash password
        hashed_pswd = pbkdf2_sha256.hash(password)

        #
        # check username same as limit 1
        # user_object = User.query.filter_by(username=username).first()
        # user_object.password gets query
        # if user_object:
        #    return "Someone else has taken this username!"

        # add user to database
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login', 'success')
        return redirect(url_for('login'))

    return render_template("registrationStudent.html", form=reg_form)

#logout route
@app.route("/logout", methods=['GET'])
def logout():

    logout_user()
    flash('You logged out!','success')
    return redirect(url_for('login'))

#route for chat - displays public rooms and form to join(create rooms)
@app.route("/chat", methods=['GET','POST'])
def chat():

    room_form = RoomCreate()
    if room_form.validate_on_submit():
        session['roomName'] = room_form.room_made.data
        session['userName'] = current_user.username
        #session['userName'] = current_user.username
        return redirect(url_for('.private_chat'))
    #elif request.method == 'GET':
    #    room_form.room_made.data = session.get('roomName', '')

    return render_template('chat_join.html', username=current_user.username, rooms=ROOMS, form=room_form)

#route for private chat established in chat route
@app.route("/private", methods=['GET','POST'])
def private_chat():

    roomName = session.get('roomName')
    userName = session.get('userName')
    message_object = Message.query.all()

    return render_template('private_room.html', userName=userName, roomName=roomName, message_object=message_object)

#route for profile
@app.route("/profile/", methods=['GET','POST'])
def profile():
    user_object = User.query.filter_by(username=current_user.username).first()

    firstname = user_object.firstname
    lastname = user_object.lastname
    email = user_object.email
    return render_template('profile.html', username=current_user.username, firstname=firstname, lastname=lastname, email=email)

#
##
### socket.io events for private chat
##
#

@socketio.on('joined', namespace='/chat')
def joined(data):
    room = session.get('roomName')
    join_room(room)
    emit('status', {'msg': current_user.username + ' has entered the room.'}, room=room)

#sends message to room
@socketio.on('text', namespace='/chat')
def text(data):
    room = session.get('roomName')
    #userName = session.get['userName']
    message = Message(message=data['msg'], username=current_user.username, room=room)
    #message = History(message=data['msg'])
    db.session.add(message)
    db.session.commit()
    emit('message', {'msg': current_user.username + ' : ' + data['msg'] + ' : ' + room}, room=room)

#leaves room
@socketio.on('left', namespace='/chat')
def left(data):
    room = session.get('roomName')
    leave_room(room)
    print('Connection on ' + room + ' with user ' + current_user.username + 'has been lost')
    emit('status', {'msg': current_user.username + ' has left the room.'}, room=room)

#connection log print message
@socketio.on('connect', namespace='/chat')
def on_connect():
    room = session.get('roomName')
    print('New connection on ' + room + ' with user ' + current_user.username + ' established')

#
#@socketio.on('disconnect', namespace='/chat')
#def on_disconnect():
#    room = session.get('roomName')
#    print(+ current_user.username + ' has disconnected from ' + room + 'at this time')


#closes room - tutor only
@socketio.on('close_room', namespace='/chat')
def close_room(data):
    room = session.get('roomName')
    print('Tutor ' + current_user.username + ' has closed Room: ' + room + ' so fuck off')

#
##
### public socketio chat events
##
#

@socketio.on('message')
def message(data):
    room = session.get('roomName')
    message = Message(message=data['msg'], username=data['username'], room=data['room'])
    db.session.add(message)
    db.session.commit()

    #send(data['room'])

    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])

    #send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])
    #current_user.username
    #emit('some-event', 'this is a custom event message')

@socketio.on('join')
def join(data):
    join_room(data['room'])
    #message_object = Message.query.filter_by(room='room').all()
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])

if __name__ == '__main__':
    socketio.run(app)
