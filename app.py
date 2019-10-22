from time import localtime, strftime
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from io import BytesIO

import os

from flask_uploads import UploadSet, configure_uploads, IMAGES, send_from_directory

from flask_forms import *
from sqlalq_datamodels import *

###     AUTHOR: AUSTIN PAUL
###     DATE: OCT 21
###     QUICKFIX_IO DIRTYBITS
###     SPRINT 6 OCT 21 BUILD DEPLOYED AT
###     quickfix-io.herokuapp.com

# socketio init
socketio = SocketIO(app)

# used for profile photos
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/pictures'
configure_uploads(app, photos)

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

        # session['userName'] = user_object.username
        session['userRole'] = user_object.role

        if user_object.role == "A":

            return redirect(url_for('admin'))

        else:

            return redirect(url_for('home'))

    return render_template("login.html", form=login_form)

# logout route
@app.route("/logout", methods=['GET'])
def logout():

    #sets status to offline at logout
    this_user = User.query.filter_by(username=current_user.username).first()
    this_user.status = 0
    db.session.commit()

    logout_user()
    flash('You logged out!', 'success')
    return redirect(url_for('login'))

#### admin route, will contain links to all users info etc
@app.route('/admin')
def admin():

    if session["userRole"] != "A":
        return "You are not an authorized admin please go back"

    users_list = User.query.all()
    all_files = FileUpload.query.all()
    blog_posts = RoomPost.query.all()
    tutors = Tutor.query.filter_by(tutor_status="pending").all()
    tutors_approved = Tutor.query.filter_by(tutor_status="approved").all()

    this_user = User.query.filter_by(username=current_user.username).first()

    return render_template("admin.html", username=current_user.username, users_list=users_list, all_files=all_files, blog_posts=blog_posts, tutors=tutors, this_user=this_user, tutors_approved=tutors_approved)

### need to rename/refactor to user
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

        user_photo = "default.jpg"

        # add user to database
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=hashed_pswd, user_photo=user_photo)
        db.session.add(user)
        db.session.commit()

        user_added = User.query.filter_by(username=username).first()
        user_id = user_added.id

        # add student to db
        student = Student(user_id=user_id)
        db.session.add(student)
        db.session.commit()

        flash('Registered successfully. Please login', 'success')
        return redirect(url_for('login'))

    return render_template("register_now.html", form=reg_form)

### tutor application/registration page
@app.route('/tutor_register', methods=['GET', 'POST'])
def new_tutor():
    this_user = User.query.filter_by(username=current_user.username).first()
    tutor_form = TutorForm()
    # Updates database if validation is successful
    if tutor_form.validate_on_submit():
        about_tutor = tutor_form.about_tutor.data

        credentials_file = request.files[tutor_form.credentials_file.name]

        user_object = User.query.filter_by(username=current_user.username).first()

        tutor_added = Tutor(user_id=user_object.id, about_tutor=about_tutor, application_comments="nothing to add", tutor_status="pending", credentials_file_name=credentials_file.filename, credentials_file_data=credentials_file.read())
        db.session.add(tutor_added)
        db.session.commit()
        flash('Registered successfully. Please login', 'success')
        return redirect(url_for('home'))

    return render_template("tutor_application.html", form=tutor_form, this_user=this_user)

### check tutor application
@app.route('/check_application', methods=['GET', 'POST'])
def check_application():

    this_user = User.query.filter_by(username=current_user.username).first()
    this_tutor = Tutor.query.filter_by(user_id=this_user.id).first()

    return render_template("check_application.html", this_user=this_user, this_tutor=this_tutor)

#room page
@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room(room_id):
    room = RoomPost.query.filter_by(id=room_id).one()

    this_user = User.query.filter_by(username=current_user.username).first()

    comments = RoomComment.query.filter_by(room_id=room_id).order_by(RoomComment.date_posted.desc()).all()
    comment_form = CommentForm()

    session['roomName'] = room.room_title
    session['userName'] = current_user.username
    session['author'] = room.author

    if comment_form.validate_on_submit():
        room_id = room.id
        comment_author = current_user.username
        content = comment_form.content.data
        date_time = datetime.now()
        # add roompost to database
        comment_post = RoomComment(room_id=room_id, comment_author=comment_author, date_posted=date_time, content=content)
        db.session.add(comment_post)
        db.session.commit()

        return redirect(url_for('room', room_id=room.id))

    if current_user.role == 'S':
        rooms = RoomPost.query.filter_by(type="Offer").order_by(RoomPost.date_posted.desc()).all()
    else:
        rooms = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()

    return render_template('viewRoom.html', room=room, username=current_user.username, rooms=rooms, comment_form=comment_form, comments=comments, this_user=this_user)

#tutor creates room
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():

    post_form = RoomForm()

    user_object = User.query.filter_by(username=current_user.username)
    this_user = User.query.filter_by(username=current_user.username).first()

    if post_form.validate_on_submit():
        subtitle = post_form.subtitle.data
        title = post_form.title.data
        content = post_form.content.data
        if current_user.role == 'S':
            type = "Request"
        else:
            type = "Offer"
        author = current_user.username
        date_time = datetime.now()
        visible = True
        new_room = RoomPost(title=title, room_title=subtitle, author=author, date_posted=date_time, content=content,
                             type=type, visible=visible)

        db.session.add(new_room)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('addNewRoom.html', username=current_user.username, post_form=post_form, user_object=user_object, this_user=this_user)

# #add comment to room lobbies
# @app.route('/add_comment', methods=['GET', 'POST'])
# def add_comment():
#
#     post_form = RoomForm()
#
#     this_user = User.query.filter_by(username=current_user.username).first()
#
#     if post_form.validate_on_submit():
#         title = post_form.title.data
#         subtitle = post_form.subtitle.data
#         content = post_form.content.data
#         if current_user.role == 'S':
#             type = "Request"
#         else:
#             type = "Offer"
#         #type = post_form.type.data
#         author = current_user.username
#         date_time = datetime.now()
#
#         # add roompost to database
#         blog_post = RoomPost(title=title, room_title=subtitle, author=author, date_posted=date_time, content=content,
#                              type=type, this_user=this_user)
#
#         db.session.add(blog_post)
#         db.session.commit()
#
#         return redirect(url_for('home'))

#student post
@app.route('/studentpost/<int:studentpost_id>', methods=['GET', 'POST'])
def studentpost(studentpost_id):

    stdpost = StudentPost.query.filter_by(id=studentpost_id).one()

    this_user = User.query.filter_by(username=current_user.username).first()

    comments = PostComment.query.filter_by(post_id=studentpost_id).order_by(PostComment.date_posted.desc()).all()
    comment_form = CommentForm()

    session['postName'] = stdpost.title
    session['userName'] = current_user.username
    session['author'] = stdpost.author

    if comment_form.validate_on_submit():
        post_id = stdpost.id
        comment_author = current_user.username
        content = comment_form.content.data
        date_time = datetime.now()
        # add roompost to database
        comment_post = PostComment(post_id=studentpost_id, comment_author=comment_author, date_posted=date_time, content=content)
        db.session.add(comment_post)
        db.session.commit()

        return redirect(url_for('studentpost', studentpost_id=post_id))

    return render_template('viewStudentPost.html', post=stdpost, username=current_user.username, comment_form=comment_form, comments=comments, this_user=this_user)

#new student request help post
@app.route('/add_student_post', methods=['GET', 'POST'])
def add_student_post():

    post_form = StudentPostForm()

    user_object = User.query.filter_by(username=current_user.username)

    this_user = User.query.filter_by(username=current_user.username).first()

    if post_form.validate_on_submit():
        title = post_form.title.data
        content = post_form.content.data
        if current_user.role == 'S':
            type = "Request"
        else:
            type = "Offer"
        #type = post_form.type.data
        author = current_user.username
        date_time = datetime.now()

        # add roompost to database
        blog_post = StudentPost(title=title, author=author, date_posted=date_time, content=content,
                             type=type)

        db.session.add(blog_post)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('addNewStudentPost.html', username=current_user.username, post_form=post_form, user_object=user_object, this_user=this_user)

#add comment to student post
# @app.route('/add_student_comment', methods=['GET', 'POST'])
# def add_student_comment():
#
#     post_form = StudentPostForm()
#
#     this_user = User.query.filter_by(username=current_user.username).first()
#
#     if post_form.validate_on_submit():
#         title = post_form.title.data
#         content = post_form.content.data
#         if current_user.role == 'S':
#             type = "Request"
#         else:
#             type = "Offer"
#         #type = post_form.type.data
#         author = current_user.username
#         date_time = datetime.now()
#
#         # add roompost to database
#         blog_post = StudentPost(title=title,  author=author, date_posted=date_time, content=content,
#                              type=type, this_user=this_user)
#
#         db.session.add(blog_post)
#         db.session.commit()
#
#         return redirect(url_for('home'))

#all users page
@app.route("/users", methods=['GET', 'POST'])
def all_users():

    all_tutors = User.query.filter_by(role='T').all()
    online_tutors = User.query.filter_by(status=1, role='T').all()
    busy_tutors = User.query.filter_by(status=2, role='T').all()
    student_users = User.query.filter_by(role='S').all()
    this_user = User.query.filter_by(username=current_user.username).first()

    return render_template('all_users.html', username=current_user.username, all_tutors=all_tutors,
                           online_tutors=online_tutors, busy_tutors=busy_tutors, student_users=student_users, this_user=this_user)

# route for chat - displays public rooms and form to join(create rooms)
@app.route("/home", methods=['GET', 'POST'])
def home():

    date_stamp = strftime('%A, %B %d', localtime())
    this_user = User.query.filter_by(username=current_user.username).first()

    one = 1
    online_users = User.query.filter_by(status=one).all()

    t_status = "not sure"

    if this_user.role == 'S':
        posts = RoomPost.query.filter_by(type="Offer").filter_by(visible=True).order_by(RoomPost.date_posted.desc()).all()
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    else:
        posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status


    offerhelp = RoomPost.query.filter_by(type="Offer").filter_by(visible=True).order_by(RoomPost.date_posted.desc()).all()
    askforhelp = StudentPost.query.order_by(StudentPost.date_posted.desc()).all()

    return render_template('home_page.html', username=current_user.username, role=current_user.role, date_stamp=date_stamp,
                           online_users=online_users, posts=posts, offerhelp=offerhelp, askforhelp=askforhelp, role_name=role_name, this_user=this_user, t_status=t_status)


# route for chat - displays public rooms and form to join(create rooms)
@app.route("/private_session/", methods=['GET', 'POST'])
def private_chat():

    date_stamp = strftime('%A, %B %d', localtime())
    connected_stamp = strftime('%I : %M %p', localtime())
    this_user = User.query.filter_by(username=current_user.username).first()

    role_name = this_user.role

    roomName = session.get('roomName')
    authorName = session.get('author')

    message_object = Message.query.filter_by(room=roomName).order_by(Message.id.asc()).all()
    room_files = RoomUpload.query.filter_by(room_name=roomName).all()
    room_object = RoomPost.query.filter_by(room_title=roomName).first()

    roomVisible = room_object.visible

    print(roomVisible)

    file_form = FileUploadForm()

    if file_form.validate_on_submit():
        file = request.files[file_form.file.name]
        newFile = RoomUpload(file_name=file.filename, room_name=roomName, username=current_user.username, data=file.read())
        db.session.add(newFile)
        db.session.commit()
        return redirect(url_for('private_chat'))

    return render_template('private_chat.html', username=current_user.username, date_stamp=date_stamp,
                           roomName=roomName, message_object=message_object,
                           authorName=authorName, connected_stamp=connected_stamp, file_form=file_form, room_files=room_files, room=room_object, this_user=this_user, role_name=role_name, roomVisible=roomVisible)

# route for personal profile
@app.route("/profile/", methods=['GET', 'POST'])
def profile():

    user_object = User.query.filter_by(username=current_user.username).first()
    this_user = User.query.filter_by(username=current_user.username).first()

    status = user_object.status
    role = user_object.role
    image_fp = user_object.user_photo

    setdbstatus = status

    #profile picture form
    image_form = ImageUploadForm()

    if image_form.validate_on_submit():

        image_filename = photos.save(request.files[image_form.image.name])
        #user_object2 = User.query.filter_by(username=current_user.username).update(dict(user_photo=os.path.join(app.config['UPLOADED_PHOTOS_DEST'], image_filename)))
        user_object2 = User.query.filter_by(username=current_user.username).update(dict(user_photo=image_filename))
        db.session.commit()

        return redirect(url_for('profile'))

    if role == "S":
        role_name = "Student"
    else:
        role_name = "Tutor"

    room_posts = RoomPost.query.filter_by(author=current_user.username).order_by(RoomPost.date_posted.desc()).all()

    user_files = FileUpload.query.filter_by(username=current_user.username).all()

    if status == 0:
        status_string = "Offine"
    elif status == 1:
        status_string = "Online"
    elif status == 2:
        status_string = "Busy"

    #file uploads
    file_form = FileUploadForm()

    if file_form.validate_on_submit():
        file = request.files[file_form.file.name]
        new_file = FileUpload(file_name=file.filename, username=current_user.username, data=file.read())
        db.session.add(new_file)
        db.session.commit()
        return redirect(url_for('profile'))

    #online status form
    ts_form = TutorStatus()

    if ts_form.validate_on_submit():
        s1 = ts_form.status.data
        print(s1)

        if(s1 == '0'):
            setdbstatus = 0
            status_string = 'Offline'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()
        if(s1 == '1'):
            setdbstatus = 1
            status_string = 'Online'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()
        if(s1 == '2'):
            setdbstatus = 2
            status_string = 'Busy'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()

    return render_template('profile.html', username=current_user.username, image_fp=image_fp, status_string=status_string, room_posts=room_posts, role_name=role_name, file_form=file_form, user_files=user_files, image_form=image_form, user_object=user_object, this_user=this_user, status=status, ts_form=ts_form, setdbstatus=setdbstatus)

#
# public profile accessed by users from online user links.
#
@app.route("/profile/<username>", methods=['GET', 'POST'])
def pub_profile(username):

    thisUser = current_user.username
    user_object = User.query.filter_by(username=username).first()

    this_user = User.query.filter_by(username=current_user.username).first()

    image_form = ImageUploadForm()

    if image_form.validate_on_submit():
        image_filename = photos.save(request.files[image_form.image.name])
        user_object2 = User.query.filter_by(username=current_user.username).update(dict(user_photo=image_filename))
        db.session.commit()

        return redirect(url_for('pub_profile'))

    user_files = FileUpload.query.filter_by(username=user_object.username).all()

    firstname = user_object.firstname
    lastname = user_object.lastname
    email = user_object.email
    status = user_object.status
    role = user_object.role

    room_posts = RoomPost.query.filter_by(author=username).order_by(RoomPost.date_posted.desc()).all()

    if role == "S":
        role_name = "Student"
    else:
        role_name = "Tutor"

    if status == 0:
        status_string = "Offline"
    elif status == 1:
        status_string = "Online"
    elif status == 2:
        status_string = "Busy"

    return render_template('pub_profile.html', thisUser=thisUser, username=username, firstname=firstname,
                           lastname=lastname, email=email, status_string=status_string, room_posts=room_posts,
                           role_name=role_name, image_form=image_form, user_object=user_object, user_files=user_files, this_user=this_user)
#gets profile pics
@app.route('/static/pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)
#download room file from chat page
@app.route('/download_room/<string:dl_name>/')
def room_download(dl_name):
    #file_data = FileUpload.query.first()ffd
    file_data = RoomUpload.query.filter_by(file_name=dl_name).first()

    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)
#download user file on profile page
@app.route('/download/<string:dl_name>/')
def download(dl_name):
    #file_data = FileUpload.query.first()
    file_data = FileUpload.query.filter_by(file_name=dl_name).first()

    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)
#download tutor credit
@app.route('/credentials/<string:dl_name>/')
def download_cred(dl_name):
    #file_data = FileUpload.query.first()
    file_data = Tutor.query.filter_by(credentials_file_name=dl_name).first()

    return send_file(BytesIO(file_data.credentials_file_data), attachment_filename=file_data.credentials_file_name, as_attachment=True)

## admin portal functions

# update room
@app.route('/updateRoom', methods=['POST'])
def updateRoom():

    room = RoomPost.query.filter_by(id=request.form['id']).first()

    room.title = request.form['name']
    room.room_title = request.form['title']
    room.content = request.form['content']
    #room.date_posted = date_time = datetime.now()
    room.date_posted = datetime.now()

    db.session.commit()

    return jsonify({'result' : 'success', "room_name" : room.room_title})

# delete room
@app.route('/deleteRoom', methods=['POST'])
def deleteRoom():

    room = RoomPost.query.filter_by(id=request.form['id']).first()
    db.session.delete(room)
    db.session.commit()

    return jsonify({'result': 'success'})

# admin approves tutor
@app.route('/approveTutor', methods=['POST'])
def approveTutor():

    user = User.query.filter_by(id=request.form['id']).first()
    tutor = Tutor.query.filter_by(user_id=user.id).first()
    user.role = "T"
    tutor.tutor_status = "approved"
    db.session.commit()

    student = Student.query.filter_by(user_id=user.id).first()
    db.session.delete(student)
    db.session.commit()
    tutor1 = Tutor.query.filter_by(user_id=user.id).first()

    return jsonify({'result' : 'success'})


#admin denies tutor
@app.route('/denyTutor', methods=['POST'])
def denyTutor():

    user = User.query.filter_by(id=request.form['id']).first()

    tutor = Tutor.query.filter_by(user_id=user.id).first()
    tutor.application_comments = request.form['comments']
    tutor.tutor_status = "denied"

    db.session.commit()

    return jsonify({'result' : 'success'})

## tutor chat room controls

# tutor makes room private
@app.route('/privateRoom', methods=['POST'])
def privateRoom():

    room = RoomPost.query.filter_by(id=request.form['id']).first()
    room.visible = False
    db.session.commit()

    #sets rooms tutor status to busy
    room_tutor = User.query.filter_by(username=room.author).first()
    room_tutor.status = 2
    db.session.commit()

    return jsonify({'result' : 'success'})


# tutor makes room private
@app.route('/publicRoom', methods=['POST'])
def publicRoom():

    room = RoomPost.query.filter_by(id=request.form['id']).first()
    room.visible = True
    db.session.commit()

    # sets rooms tutor status to online
    room_tutor = User.query.filter_by(username=room.author).first()
    room_tutor.status = 1
    db.session.commit()

    return jsonify({'result' : 'success'})


#
###
### private_chat socket io functions - private_chat.html file
##
#

#when user sends message
@socketio.on('message')
def message(data):
    room = session.get('roomName')
    message_time = strftime('%I:%M%p %m-%d-%Y', localtime())
    message = Message(message=data['msg'], username=data['username'], room=data['room'], created_at=message_time)
    db.session.add(message)
    db.session.commit()

    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())},
         room=data['room'])

#ran when joining room
@socketio.on('join')
def join(data):
    room = session.get('roomName')
    #join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been established')
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])

#when uploading a file
@socketio.on('upload')
def upload(data):
    room = session.get('roomName')
    #join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' uploaded a file to ' + data['room'] + " room")
    send({'msg': data['username'] + " sent a file to the " + data['room'] + " room."}, room=data['room'])

#when tutor makes room private
@socketio.on('private')
def private(data):
    room = session.get('roomName')
    #join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' has now started a private session in room' + data['room'])
    send({'msg': "Tutor " + data['username'] + " has now made the " + data['room'] + " room private."}, room=data['room'])

#when tutor makes room public
@socketio.on('public')
def public(data):
    room = session.get('roomName')
    #join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' has now ended a private session in room' + data['room'])
    send({'msg': "Tutor " + data['username'] + " has now made the " + data['room'] + " room public."}, room=data['room'])

#when user leaves room
@socketio.on('leave')
def leave(data):
    room = session.get('roomName')
    leave_room(room)
    #leave_room(data['room'])
    session['roomName'] = " "
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been lost')
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])

#when tutor closes room
@socketio.on('close_room')
def close_room(data):
    #room = data['room']
    room = session.get('roomName')
    print('Tutor ' + current_user.username + ' has closed Room: ' + room + '.')


if __name__ == '__main__':
    socketio.run(app)
    #app.run()
    # ^ uncomment this when running and comment out socketio.run(app) at deployment