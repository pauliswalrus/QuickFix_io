from time import localtime, strftime
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from io import BytesIO
import random

from app.wtform_fields import *
from app.dataModel import *

###     AUTHOR: AUSTIN PAUL
###     DATE: SEPT 27 2019
###     QUICKFIX_IO DIRTYBITS
###     POST-SPRINT 3 BUILD

# socketio init
socketio = SocketIO(app)

# rooms used at chat
ROOMS = ["lounge", "student chat", "coding q & a", "general math"]

# creates and inits Login
login = LoginManager(app)
login.init_app(app)


# loads in user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# main route login
@app.route('/', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)

        if user_object.role == "A":

            return redirect(url_for('admin'))

        else:

            return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)

#### admin route, will contain links to all users info etc
@app.route('/admin')
def admin():


    users_list = User.query.all()

    all_files = FileUpload.query.all()

    blog_posts = BlogPost.query.all()

    return render_template("admin.html", username=current_user.username, users_list=users_list, all_files=all_files, blog_posts=blog_posts)
#
##
###pulls up register page - currently users only
##
#

@app.route('/register', methods=['GET', 'POST'])
def new_student():
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

        # add user to database
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login', 'success')
        return redirect(url_for('login'))

    return render_template("registrationStudent.html", form=reg_form)


# Use this to try both forms
@app.route('/register2', methods=['GET', 'POST'])
def new_student_test():

    # Tutor Register Form from wtform_fields.py
    tut_form = TutorRegistrationForm()

    # Updates database if validation is successful
    if tut_form.validate_on_submit():
        tutor_username = tut_form.username.data
        tutor_firstname = tut_form.firstname.data
        tutor_lastname = tut_form.lastname.data
        tutor_email = tut_form.email.data
        tutor_workplace = tut_form.workplace.data
        tutor_occupation = tut_form.occupation.data
        tutor_password = tut_form.password.data

        # hash password
        tutor_password_hashed = pbkdf2_sha256.hash(tutor_password)

        ################## TO DO: Add Tutor to DB ##################

    # Student Register Form from wtform_fields.py
    stud_form = StudentRegistrationForm()

    # Updates database if validation is successful
    if stud_form.validate_on_submit():
        student_username = stud_form.username.data
        student_firstname = stud_form.firstname.data
        student_lastname = stud_form.lastname.data
        student_email = stud_form.email.data
        student_password = stud_form.password.data

        # hash password
        student_password_hashed = pbkdf2_sha256.hash(student_password)

    # reg_forum from wtform_fields.py
    #original below:
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

        # add user to database
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=hashed_pswd)
        db.session.add(user)
        db.session.commit()

        flash('Registered successfully. Please login', 'success')
        return redirect(url_for('login'))

    return render_template("registrationStudent.html", form=reg_form, tut_form=tut_form, stud_form=stud_form)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = BlogPost.query.filter_by(id=post_id).one()

    session['roomName'] = post.subtitle
    session['userName'] = current_user.username
    session['author'] = post.author
    return render_template('post.html', post=post, username=current_user.username)


@app.route('/add', methods=['GET', 'POST'])
def add_post():
    post_form = BlogPostForm()

    if post_form.validate_on_submit():
        title = post_form.title.data
        subtitle = post_form.subtitle.data
        content = post_form.content.data
        type = post_form.type.data
        author = current_user.username
        date_time = datetime.now()

        # add blogpost to database
        blog_post = BlogPost(title=title, subtitle=subtitle, author=author, date_posted=date_time, content=content,
                             type=type)

        db.session.add(blog_post)
        db.session.commit()

        return redirect(url_for('chat'))

    return render_template('add.html', username=current_user.username, post_form=post_form)


# logout route
@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    flash('You logged out!', 'success')
    return redirect(url_for('login'))


@app.route("/users", methods=['GET', 'POST'])
def all_users():
    all_tutors = User.query.filter_by(role='T').all()

    online_tutors = User.query.filter_by(status=1, role='T').all()

    student_users = User.query.filter_by(role='S').all()

    return render_template('all_users.html', username=current_user.username, all_tutors=all_tutors,
                           online_tutors=online_tutors, student_users=student_users)


# route for chat - displays public rooms and form to join(create rooms)
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    date_stamp = strftime('%A, %B %d', localtime())
    user_now = current_user.username
    # print(user_now)

    this_user = User.query.filter_by(username=current_user.username).first()

    one = 1
    online_users = User.query.filter_by(status=one).all()

    # checks if Role is student, this only allows
    if this_user.role == 'S':
        posts = BlogPost.query.filter_by(type="Offer").order_by(BlogPost.date_posted.desc()).all()
    else:
        posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).all()

    return render_template('chat_join.html', username=current_user.username, rooms=ROOMS, date_stamp=date_stamp,
                           online_users=online_users, posts=posts)


# route for chat - displays public rooms and form to join(create rooms)
@app.route("/private_session/", methods=['GET', 'POST'])
def chat_jq():
    date_stamp = strftime('%A, %B %d', localtime())
    user_now = current_user.username

    roomName = session.get('roomName')

    authorName = session.get('author')

    message_object = Message.query.filter_by(room=roomName).order_by(Message.id.desc()).all()
    # print(user_now)

    private_form = RoomJoin()
    if private_form.validate_on_submit():
        post_Room = session.get('roomName')
        print(post_Room)

        delpost = BlogPost.query.filter_by(subtitle=post_Room).first()
        db.session.delete(delpost)
        db.session.commit()

    return render_template('private_jq.html', username=current_user.username, rooms=ROOMS, date_stamp=date_stamp,
                           roomName=roomName, message_object=message_object, private_form=private_form,
                           authorName=authorName)


# no longer used!
# @app.route("/private", methods=['GET', 'POST'])
# def private_chat():
#     roomName = session.get('roomName')
#     userName = session.get('userName')
#     # message_object = Message.query.all()
#
#     message_object = Message.query.filter_by(room=roomName).all()
#
#     room_form = RoomJoin()
#     if room_form.validate_on_submit():
#         delpost = BlogPost.query.filter_by(subtitle=roomName).first()
#         db.delete(delpost)
#         db.commit()
#         redirect(url_for('chat'))
#
#     return render_template('private_room.html', userName=userName, roomName=roomName, message_object=message_object,
#                            room_form=room_form)
#

# route for profile
@app.route("/profile/", methods=['GET', 'POST'])
def profile():
    user_object = User.query.filter_by(username=current_user.username).first()

    firstname = user_object.firstname
    lastname = user_object.lastname
    email = user_object.email
    status = user_object.status
    role = user_object.role

    if role == "S":
        role_name = "Student"
    else:
        role_name = "Tutor"

    blog_posts = BlogPost.query.filter_by(author=current_user.username).order_by(BlogPost.date_posted.desc()).all()

    if status == 0:
        status_string = "Offine"
    elif status == 1:
        status_string = "Online"

    user_files = FileUpload.query.filter_by(username=current_user.username).all()

    file_form = FileUploadForm()

    if file_form.validate_on_submit():
        file = request.files[file_form.file.name]
        newFile = FileUpload(file_name=file.filename, username=current_user.username, data=file.read())
        db.session.add(newFile)
        db.session.commit()

    return render_template('profile.html', username=current_user.username, firstname=firstname, lastname=lastname,
                           email=email, status_string=status_string, blog_posts=blog_posts, role_name=role_name, file_form=file_form, user_files=user_files)

@app.route('/download')
def download():
    #file_data = FileUpload.query.first()
    file_data = FileUpload.query.filter_by(username=current_user.username).first()

    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)

# public profile accessed by users from online user links.
@app.route("/profile/<username>", methods=['GET', 'POST'])
def pub_profile(username):
    thisUser = current_user.username
    user_object = User.query.filter_by(username=username).first()

    firstname = user_object.firstname
    lastname = user_object.lastname
    email = user_object.email
    status = user_object.status
    role = user_object.role

    if role == "S":
        role_name = "Student"
    else:
        role_name = "Tutor"

    blog_posts = BlogPost.query.filter_by(author=username).order_by(BlogPost.date_posted.desc()).all()

    if status == 0:
        status_string = "Offine"
    elif status == 1:
        status_string = "Online"

    return render_template('pub_profile.html', thisUser=thisUser, username=username, firstname=firstname,
                           lastname=lastname, email=email, status_string=status_string, blog_posts=blog_posts,
                           role_name=role_name)


#
## file upload test
#

# @app.route('/upload', methods=['GET','POST'])
# def upload():
#
# #     file = request.files['inputFile']
# #
# #     print(file.filename)
# # #
# #     newFile = FileUpload(name=file.filename, data=file.read())
# #     db.session.add(newFile)
# #     db.session.commit()
#
#     return file.filename

#
# ##
# ### socket.io events for private chat redundant, used in private_room.html
# ##
# #

# joins room
@socketio.on('joined', namespace='/chat')
def joined(data):
    room = session.get('roomName')
    join_room(room)
    emit('status', {'msg': current_user.username + ' has entered the room ' + room}, room=room)


# sends message to room
@socketio.on('text', namespace='/chat')
def text(data):
    room = session.get('roomName')
    username = session.get('userName')
    message_time = strftime('%b-%d %I:%M%p', localtime())
    message = Message(message=data['msg'], username=username, room=room)
    # message = History(message=data['msg'])
    db.session.add(message)
    db.session.commit()
    emit('message', {'msg': username + ' : ' + data['msg'] + ' : ' + room + ': ' + message_time}, room=room)


# leaves room
@socketio.on('left', namespace='/chat')
def left(data):
    room = session.get('roomName')
    leave_room(room)
    session['roomName'] = " "
    print('Connection on ' + room + ' with user ' + current_user.username + ' has been lost')
    emit('status', {'msg': current_user.username + ' has left the room ' + room}, room=room)


# connection log print message
@socketio.on('connect', namespace='/chat')
def on_connect():
    room = session.get('roomName')
    userName = session.get('userName')
    print('Connection on ' + room + ' with user ' + userName + ' has been established')


# closes room - tutor only
@socketio.on('close_room', namespace='/chat')
def close_room(data):
    room = session.get('roomName')
    print('Tutor ' + current_user.username + ' has closed Room: ' + room + '.')


#
###
### public socketio chat events join_chat.html - socketio.js file
##
#

@socketio.on('message')
def message(data):
    room = session.get('roomName')
    message_time = strftime('%I:%M%p %m-%d-%Y', localtime())
    message = Message(message=data['msg'], username=data['username'], room=data['room'], created_at=message_time)
    db.session.add(message)
    db.session.commit()

    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())},
         room=data['room'])


@socketio.on('join')
def join(data):
    join_room(data['room'])
    # message_object = Message.query.filter_by(room='room').all()
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been established')
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been lost')
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])


@socketio.on('close_room')
def close_room(data):
    room = data['room']
    print('Tutor ' + current_user.username + ' has closed Room: ' + room + '.')


if __name__ == '__main__':
    socketio.run(app)
