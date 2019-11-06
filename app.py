from time import localtime, strftime
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, session, request, send_file, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from io import BytesIO
from flask_bootstrap import Bootstrap
import os

from flask_uploads import UploadSet, configure_uploads, IMAGES, send_from_directory

from flask_forms import *
from sqlalq_datamodels import *


############################################################################################################
##
# AUTHOR: AUSTIN PAUL, EMMA HOBDEN, HALEY WALBOURNE
# QUICKFIX_IO DIRTYBITS
# PRESENTATION 1 BUILD DEPLOYED AT
# quickfix-io.herokuapp.com
##
############################################################################################################

# socketio init
socketio = SocketIO(app)

# used for profile photos
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/pictures'
configure_uploads(app, photos)

# creates and inits Login
login = LoginManager(app)
login.init_app(app)

Bootstrap(app)

# loads in user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


############################################################################################################
##
# BASIC PAGES / FUNCTIONS
##
############################################################################################################


# Login Page/Function
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
            # sets status to online at login
            user_object.status = 1
            db.session.commit()

            return redirect(url_for('home'))

    return render_template("login.html", form=login_form)


# Logout Function
@app.route("/logout", methods=['GET'])
def logout():
    # sets status to offline at logout
    this_user = User.query.filter_by(username=current_user.username).first()
    this_user.status = 0
    db.session.commit()

    logout_user()
    # flash('You logged out!', 'success')
    return redirect(url_for('login'))


# Registration Page/Function
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
        user = User(username=username, firstname=firstname, lastname=lastname, email=email, password=hashed_pswd,
                    user_photo=user_photo)
        db.session.add(user)
        db.session.commit()

        user_added = User.query.filter_by(username=username).first()
        user_id = user_added.id

        # add student to db
        student = Student(user_id=user_id)
        db.session.add(student)
        db.session.commit()

        # flash('Registered successfully. Please login', 'success')
        return redirect(url_for('login'))

    return render_template("register_now.html", form=reg_form)


# Home Page
@app.route("/home", methods=['GET', 'POST'])
def home():
    date_stamp = strftime('%A, %B %d', localtime())
    this_user = User.query.filter_by(username=current_user.username).first()

    online_users = User.query.filter_by(status=1, role="T").all()

    t_status = "not sure"

    if this_user.role == 'S':
        posts = RoomPost.query.filter_by(type="Offer").filter_by(visible=True).order_by(
            RoomPost.date_posted.desc()).all()
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()
        role_name = "Admin"
        t_status = "Admin"

    offerhelp = RoomPost.query.filter_by(type="Offer").filter_by(visible=True).order_by(
        RoomPost.date_posted.desc()).all()
    askforhelp = StudentPost.query.order_by(StudentPost.date_posted.desc()).all()

    return render_template('home_page.html', username=current_user.username, role=current_user.role,
                           date_stamp=date_stamp,
                           online_users=online_users, posts=posts, offerhelp=offerhelp, askforhelp=askforhelp,
                           role_name=role_name, this_user=this_user, t_status=t_status)


############################################################################################################
##
# ADMIN PAGES / FUNCTIONS
##
############################################################################################################

# View Pending Tutor Applications
@app.route('/admin')
def admin():
    if session["userRole"] != "A":
        return "You are not an authorized admin. Please go back."

    # users in desc order
    users_list = User.query.order_by(User.id.desc()).all()
    all_files = FileUpload.query.all()

    # rooms desc by date - refactor to rooms
    blog_posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()

    tutors = Tutor.query.filter_by(tutor_status="pending").all()


    # grabs all pending tutors, grabs info from User and Tutor table
    tutors_pending = db.session.query(User.firstname, User.lastname, User.username, Tutor.user_id, Tutor.tutor_id,
                                      Tutor.about_tutor, Tutor.tutor_status, Tutor.credentials_file_name,
                                      Tutor.application_comments).filter(User.id == Tutor.user_id,
                                                                         Tutor.tutor_status == "pending").order_by(
        Tutor.tutor_id.desc()).all()
    # tutors_approved = Tutor.query.filter_by(tutor_status="approved").all()

    # approved tutors in desc order
    tutors_approved = db.session.query(User.firstname, User.lastname, User.username, Tutor.user_id, Tutor.tutor_id,
                                       Tutor.about_tutor, Tutor.tutor_status, Tutor.credentials_file_name,
                                       Tutor.application_comments).filter(User.id == Tutor.user_id).order_by(User.id.desc()).all()

    this_user = User.query.filter_by(username=current_user.username).first()

    return render_template("admin.html", username=current_user.username, users_list=users_list, all_files=all_files,
                           blog_posts=blog_posts, tutors=tutors, this_user=this_user, tutors_approved=tutors_approved,
                           tutors_pending=tutors_pending)


# View Approved Tutor Applications
@app.route('/admin_approved')
def admin_approved():
    if session["userRole"] != "A":
        return "You are not an authorized admin. Please go back."

    this_user = User.query.filter_by(username=current_user.username).first()

    # approved tutors in desc order
    tutors_approved = db.session.query(User.firstname, User.lastname, User.username, Tutor.user_id, Tutor.tutor_id,
                                       Tutor.about_tutor, Tutor.tutor_status, Tutor.credentials_file_name,
                                       Tutor.application_comments).filter(User.id == Tutor.user_id, Tutor.tutor_status == 'approved').order_by(
        User.id.desc()).all()

    tutor_courses = TutorCourses.query.filter_by(user_id=this_user.id).all()

    return render_template("admin_approved.html", this_user=this_user, tutors_approved=tutors_approved, tutor_courses=tutor_courses)


# Download Tutor Credentials
@app.route('/credentials/<string:dl_name>/')
def download_cred(dl_name):
    # file_data = FileUpload.query.first()
    file_data = Tutor.query.filter_by(credentials_file_name=dl_name).first()

    return send_file(BytesIO(file_data.credentials_file_data), attachment_filename=file_data.credentials_file_name,
                     as_attachment=True)


# Approve Tutor
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

    return jsonify({'result': 'success'})


# Deny Tutor
@app.route('/denyTutor', methods=['POST'])
def denyTutor():
    user = User.query.filter_by(id=request.form['id']).first()

    tutor = Tutor.query.filter_by(user_id=user.id).first()
    tutor.application_comments = request.form['comments']
    tutor.tutor_status = "denied"
    db.session.commit()

    return jsonify({'result': 'success'})


# Delete Tutor Application (redirects to new application)
@app.route('/deleteApplication', methods=['POST'])
def deleteApplication():
    user = User.query.filter_by(username=current_user.username).first()

    db.session.query(TutorCourses).filter_by(user_id=user.id).delete()
    db.session.commit()

    tutor = Tutor.query.filter_by(user_id=user.id).first()
    db.session.delete(tutor)
    db.session.commit()

    return redirect(url_for('application_begin'))


# Manage Users
@app.route("/users", methods=['GET', 'POST'])
def all_users():
    if session["userRole"] != "A":
        return "You are not an authorized admin. Please go back."

    # users in desc order
    users_list = User.query.order_by(User.id.desc()).all()

    all_tutors = User.query.filter_by(role='T').all()
    online_tutors = User.query.filter_by(status=1, role='T').all()
    busy_tutors = User.query.filter_by(status=2, role='T').all()
    student_users = User.query.filter_by(role='S').all()

    this_user = User.query.filter_by(username=current_user.username).first()

    return render_template('all_users.html', username=current_user.username, all_tutors=all_tutors,
                           online_tutors=online_tutors, busy_tutors=busy_tutors, student_users=student_users,
                           this_user=this_user, users_list=users_list)


# Edit User
@app.route('/editUser', methods=['POST'])
def editUser():
    user_edit = User.query.filter_by(id=request.form['id']).first()

    user_edit.username = request.form['username']
    user_edit.firstname = request.form['firstname']
    user_edit.lastname = request.form['lastname']
    user_edit.email = request.form['email']

    db.session.commit()

    return jsonify({'result': 'success'})


# Delete User
@app.route('/deleteUser', methods=['POST'])
def deleteUser():
    user = User.query.filter_by(id=request.form['id']).first()

    #deletes all trace of users
    db.session.query(RoomPost).filter_by(author=user.username).delete()
    db.session.commit()
    db.session.query(StudentPost).filter_by(author=user.username).delete()
    db.session.commit()
    db.session.query(PostComment).filter_by(comment_author=user.username).delete()
    db.session.commit()
    db.session.query(RoomComment).filter_by(comment_author=user.username).delete()
    db.session.commit()
    db.session.query(FileUpload).filter_by(username=user.username).delete()
    db.session.commit()

    if user.role == "T":
        tutor = Tutor.query.filter_by(user_id=user.id).first()
        db.session.delete(tutor)
        db.session.commit()

        db.session.delete(user)
        db.session.commit()

    elif user.role == "S":
        student = Student.query.filter_by(user_id=user.id).first()
        db.session.delete(student)
        db.session.commit()

        db.session.delete(user)
        db.session.commit()

    return jsonify({'result': 'success'})


# Manage Rooms
@app.route('/admin_rooms')
def admin_rooms():
    if session["userRole"] != "A":
        return "You are not an authorized admin. Please go back."

    this_user = User.query.filter_by(username=current_user.username).first()

    # rooms desc by date
    blog_posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()

    return render_template("admin_rooms.html", this_user=this_user, blog_posts=blog_posts)


# Delete Room
@app.route('/deleteRoom', methods=['POST'])
def deleteRoom():
    room = RoomPost.query.filter_by(id=request.form['id']).first()
    db.session.delete(room)
    db.session.commit()
    db.session.query(RoomComment).filter_by(room_id=room.id).delete()
    db.session.commit()
    db.session.query(RoomUpload).filter_by(room_name=room.title).delete()
    db.session.commit()
    db.session.query(Message).filter_by(room=room.title).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Delete Comments on Rooms
@app.route('/deleteRoomComments', methods=['POST'])
def deleteRoomComments():
    room = RoomPost.query.filter_by(id=request.form['id']).first()

    # delete all messages by room title
    db.session.query(RoomComment).filter_by(room_id=room.id).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Manage Community Forum Posts
@app.route('/admin_posts')
def admin_posts():
    if session["userRole"] != "A":
        return "You are not an authorized admin. Please go back."

    this_user = User.query.filter_by(username=current_user.username).first()

    # rooms desc by date
    forum_posts = StudentPost.query.order_by(StudentPost.date_posted.desc()).all()

    return render_template("admin_posts.html", this_user=this_user, forum_posts=forum_posts)


# Delete Community Forum Posts
@app.route('/deletePost', methods=['POST'])
def deletePost():
    post = StudentPost.query.filter_by(id=request.form['id']).first()
    db.session.delete(post)
    db.session.commit()
    db.session.query(PostComment).filter_by(post_id=post.id).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Update Community Forums Posts
@app.route('/updatePost', methods=['POST'])
def updatePost():
    post = StudentPost.query.filter_by(id=request.form['id']).first()

    post.title = request.form['title']
    post.content = request.form['content']
    # room.date_posted = date_time = datetime.now()
    post.date_posted = datetime.now()

    db.session.commit()

    # return jsonify({'result': 'success', "post_title": post.title})

    return jsonify({'result': 'success'})


# Delete Community Forum Post Comments
@app.route('/deletePostComments', methods=['POST'])
def deletePostComments():
    post = StudentPost.query.filter_by(id=request.form['id']).first()

    # delete all messages by room title
    db.session.query(PostComment).filter_by(post_id=post.id).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


############################################################################################################
##
# TUTOR SPECIFIC PAGES/FUNCTIONS
##
############################################################################################################


# Tutor Application Page - Submit
@app.route('/application_submit', methods=['GET', 'POST'])
def new_tutor():
    this_user = User.query.filter_by(username=current_user.username).first()

    t_courses = TutorCourses.query.filter_by(user_id=this_user.id).order_by(TutorCourses.tutor_course_id.desc()).all()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"
        t_status = "not sure"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            if tutor.tutor_status is None:
                t_status = "not sure"

            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    tutor_form = TutorForm()

    # Updates database if validation is successful
    if tutor_form.validate_on_submit():
        about_tutor = tutor_form.about_tutor.data
        credentials_file = request.files[tutor_form.credentials_file.name]
        user_object = User.query.filter_by(username=current_user.username).first()
        tutor_added = Tutor(user_id=user_object.id, about_tutor=about_tutor, application_comments="nothing to add",
                            tutor_status="pending", credentials_file_name=credentials_file.filename,
                            credentials_file_data=credentials_file.read())
        db.session.add(tutor_added)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("applicationSubmit.html", form=tutor_form, this_user=this_user, t_status=t_status, role_name=role_name, t_courses=t_courses)


# Check Tutor Application (accessed by applicant by navbar OR admin from portal)
@app.route('/check_application/<int:user_id>', methods=['GET', 'POST'])
def check_application(user_id):

    this_user = User.query.filter_by(id=current_user.id).first()
    app_user = User.query.filter_by(id=user_id).first()

    tutor_courses = TutorCourses.query.filter_by(user_id=app_user.id).all()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    this_tutor = Tutor.query.filter_by(user_id=app_user.id).first()

    return render_template("check_application.html", this_user=this_user, this_tutor=this_tutor, role_name=role_name, t_status=t_status, tutor_courses=tutor_courses, app_user=app_user)


# Add Tutor Courses (used in tutor_application and tutor profile)
@app.route('/addTutorCourse', methods=['POST'])
def addTutorCourse():

    user = User.query.filter_by(username=current_user.username).first()
    user_id = user.id
    this_course = ProgramCourse.query.filter_by(courseName=request.form['course_name']).first()
    tutor_course = TutorCourses(user_id=user_id, course_name=this_course.courseName,
                              course_id=this_course.program_course_id, course_code=this_course.courseCode)
    db.session.add(tutor_course)
    db.session.commit()

    return jsonify({'result': 'success'})


# Delete Tutor Courses (used in tutor application and profile)
@app.route('/clearTutorCourses', methods=['POST'])
def clearTutorCourses():

    user = User.query.filter_by(username=current_user.username).first()
    user_id = user.id

    db.session.query(TutorCourses).filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Tutor Courses Page - accessed from profile programs
@app.route("/tutor_courses/<int:program_id>", methods=['GET', 'POST'])
def tutor_courses(program_id):

    this_user = User.query.filter_by(username=current_user.username).first()
    this_tutor = Tutor.query.filter_by(user_id=this_user.id).first()
    u_courses = TutorCourses.query.filter_by(user_id=this_user.id).order_by(TutorCourses.tutor_course_id.desc()).all()
    this_program = Program.query.filter_by(program_id=program_id).first()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"


    # program = Program.query.filter_by(program_name=program_name).first()
    program_courses = ProgramCourse.query.filter_by(program_id=program_id).all()
    course_list = [(k.program_course_id, k.courseName) for k in program_courses]

    form = CourseForm()

    form.course_options.choices = course_list

    if request.method == 'GET':
        return render_template('tutorCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)

    if request.method == 'POST':
        course_picked = form.course_options.data

        this_course = ProgramCourse.query.filter_by(program_course_id=course_picked).first()
        this_user = User.query.filter_by(username=current_user.username).first()
        tutor_course = TutorCourses(user_id=this_user.id, course_name=this_course.courseName,
                                    course_id=this_course.program_course_id, course_code=this_course.courseCode)
        db.session.add(tutor_course)
        db.session.commit()

        return redirect(url_for('tutor_courses', program_id=program_id))

    return render_template('tutorCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)


# Tutor Application - Choose a Program Page
@app.route("/application_begin", methods=['GET', 'POST'])
def application_begin():

    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"
    available_programs = Program.query.all()
    program_list = [(k.program_id, k.programName) for k in available_programs]
    form1 = ProgramForm()
    form1.program_options.choices = program_list

    if request.method == 'POST':
        program_picked = form1.program_options.data
        this_program = Program.query.filter_by(program_id=program_picked).first()
        program_courses = ProgramCourse.query.filter_by(program_id=program_picked).all()

        return redirect(url_for('application_courses', program_id=program_picked))

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    return render_template('applicationBegin.html', username=current_user.username, this_user=this_user, form1=form1, role_name=role_name, t_status=t_status)


# Tutor Application Courses - accessed from application begin page
@app.route("/application_courses/<int:program_id>", methods=['GET', 'POST'])
def application_courses(program_id):

    this_user = User.query.filter_by(username=current_user.username).first()
    this_tutor = Tutor.query.filter_by(user_id=this_user.id).first()
    u_courses = TutorCourses.query.filter_by(user_id=this_user.id).order_by(TutorCourses.tutor_course_id.desc()).all()

    this_program = Program.query.filter_by(program_id=program_id).first()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"


    # program = Program.query.filter_by(program_name=program_name).first()
    program_courses = ProgramCourse.query.filter_by(program_id=program_id).all()
    course_list = [(k.program_course_id, k.courseName) for k in program_courses]

    form = CourseForm()

    form.course_options.choices = course_list

    if request.method == 'GET':
        return render_template('applicationCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)

    if request.method == 'POST':
        course_picked = form.course_options.data

        this_course = ProgramCourse.query.filter_by(program_course_id=course_picked).first()
        this_user = User.query.filter_by(username=current_user.username).first()
        tutor_course = TutorCourses(user_id=this_user.id, course_name=this_course.courseName,
                                    course_id=this_course.program_course_id, course_code=this_course.courseCode)
        db.session.add(tutor_course)
        db.session.commit()

        return redirect(url_for('application_courses', program_id=program_id))

    return render_template('applicationCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)


# Tutor - Delete Courses (used in profile and tutor application)
@app.route('/deleteTutorCourse', methods=['POST'])
def deleteTutorCourse():

    user = User.query.filter_by(username=current_user.username).first()
    user_id = user.id
    tutor_course = TutorCourses.query.filter_by(user_id=user_id, tutor_course_id=request.form['id']).first()
    db.session.delete(tutor_course)
    db.session.commit()

    return jsonify({'result': 'success'})


############################################################################################################
##
# FIND A TUTOR PAGES
##
############################################################################################################


# View All Public Tutor Rooms
@app.route('/allrooms', methods=['GET', 'POST'])
def allrooms():
    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    search_form = TutorSearchForm(request.form)

    if request.method == 'POST':
        return search_results(search_form)


    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    # room_posts = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()


    room_posts = db.session.query(User.user_photo, RoomPost.room_course, RoomPost.room_title,
                                       RoomPost.author, RoomPost.title, RoomPost.date_posted,
                                       RoomPost.content, RoomPost.id, RoomPost.room_code).filter(RoomPost.author == User.username, RoomPost.visible == True).order_by(
        RoomPost.date_posted.desc()).all()

    return render_template('tutorPosts.html', this_user=this_user, room_posts=room_posts, role_name=role_name, t_status=t_status, search_form=search_form)


# View a Specific Tutor Room (lobby)
@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room(room_id):
    room = RoomPost.query.filter_by(id=room_id).one()

    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

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

        comment_post = RoomComment(room_id=room_id, comment_author=comment_author, date_posted=date_time,
                                   content=content)
        db.session.add(comment_post)
        db.session.commit()

        return redirect(url_for('room', room_id=room.id))

    if current_user.role == 'S':
        rooms = RoomPost.query.filter_by(type="Offer").order_by(RoomPost.date_posted.desc()).all()
    else:
        rooms = RoomPost.query.order_by(RoomPost.date_posted.desc()).all()

    return render_template('viewRoom.html', room=room, username=current_user.username, rooms=rooms,
                           comment_form=comment_form, comments=comments, this_user=this_user, role_name=role_name, t_status=t_status)


# Tutor Creates New Room
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    post_form = RoomForm()

    user_object = User.query.filter_by(username=current_user.username)
    this_user = User.query.filter_by(username=current_user.username).first()
    user_courses = TutorCourses.query.filter_by(user_id=this_user.id).all()
    room_courses = [(k.course_id, k.course_name) for k in user_courses]
    post_form.room_course.choices = room_courses

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"
        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    if request.method == 'POST':
        subtitle = post_form.subtitle.data
        content = post_form.content.data
        room_course = post_form.room_course.data
        course = TutorCourses.query.filter_by(course_id=room_course).first()
        room_course_name = course.course_name
        room_code = course.course_code
        print(course.course_code)

        if current_user.role == 'S':
            type = "Request"
        else:
            type = "Offer"
        author = current_user.username
        date_time = datetime.now()
        visible = True
        new_room = RoomPost(room_title=subtitle, author=author, date_posted=date_time, content=content,
                            type=type, room_course=room_course_name, room_code=room_code, visible=visible)

        db.session.add(new_room)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('addNewRoom.html', username=current_user.username, post_form=post_form,
                           user_object=user_object, this_user=this_user, t_status=t_status, role_name=role_name)


# Find a Tutor Page - Search for a Room
@app.route('/results')
def search_results(search):
    this_user = User.query.filter_by(username=current_user.username).first()
    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    search_form = TutorSearchForm(request.form)

    results = []
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Course Code':
            # qry = db.session.query(User.user_photo, RoomPost).filter(RoomPost.room_code.contains(search_string))

            qry = db.session.query(User.user_photo, RoomPost.room_course, RoomPost.room_title,
                                          RoomPost.author, RoomPost.title, RoomPost.date_posted,
                                          RoomPost.content, RoomPost.id, RoomPost.room_code).filter(
                RoomPost.author == User.username).filter(RoomPost.room_code.contains(search_string)).order_by(RoomPost.date_posted.desc())

            results = qry.all()

        elif search.data['select'] == 'Course Name':
            qry = db.session.query(RoomPost).filter(RoomPost.room_course.contains(search_string))

            qry = db.session.query(User.user_photo, RoomPost.room_course, RoomPost.room_title,
                                   RoomPost.author, RoomPost.title, RoomPost.date_posted,
                                   RoomPost.content, RoomPost.id, RoomPost.room_code).filter(
                RoomPost.author == User.username).filter(RoomPost.room_course.contains(search_string)).order_by(RoomPost.date_posted.desc())

            results = qry.all()
        elif search.data['select'] == 'User Name':
            qry = db.session.query(RoomPost).filter(
                RoomPost.author.contains(search_string))

            qry = db.session.query(User.user_photo, RoomPost.room_course, RoomPost.room_title,
                                   RoomPost.author, RoomPost.title, RoomPost.date_posted,
                                   RoomPost.content, RoomPost.id, RoomPost.room_code).filter(
                RoomPost.author == User.username).filter(RoomPost.author.contains(search_string)).order_by(RoomPost.date_posted.desc())

            results = qry.all()
        else:
            qry = db.session.query(RoomPost)
            results = qry.all()
    else:
        qry = db.session.query(RoomPost)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/allrooms')
    else:
        # display results
        room_posts = results
        # table.border = True

        return render_template('tutorPosts.html', this_user=this_user, room_posts=room_posts, role_name=role_name, t_status=t_status, search_form=search_form)


############################################################################################################
##
# COMMUNITY FORUMS PAGES
##
############################################################################################################


# View all Community Forums Posts
@app.route('/allstudentposts', methods=['GET', 'POST'])
def allstudentposts():
    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    search_form = ForumSearchForm(request.form)

    if request.method == 'POST':
        return forum_search_results(search_form)

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    student_posts = StudentPost.query.order_by(StudentPost.date_posted.desc()).all()

    return render_template('studentPosts.html', this_user=this_user, student_posts=student_posts, role_name=role_name, t_status=t_status, search_form=search_form)


# View a Specific Community Forum Post
@app.route('/studentpost/<int:studentpost_id>', methods=['GET', 'POST'])
def studentpost(studentpost_id):

    stdpost = StudentPost.query.filter_by(id=studentpost_id).one()

    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    # student post comments
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

        comment_post = PostComment(post_id=studentpost_id, comment_author=comment_author, date_posted=date_time,
                                   content=content)
        db.session.add(comment_post)
        db.session.commit()

        return redirect(url_for('studentpost', studentpost_id=post_id))

    return render_template('viewStudentPost.html', post=stdpost, username=current_user.username,
                           comment_form=comment_form, comments=comments, this_user=this_user, t_status=t_status, role_name=role_name)


# Add a New Community Forum Post
@app.route('/add_student_post', methods=['GET', 'POST'])
def add_student_post():
    post_form = StudentPostForm()

    user_object = User.query.filter_by(username=current_user.username)
    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        user_courses = UserCourses.query.filter_by(user_id=this_user.id).all()
        post_courses = [(k.course_id, k.course_name) for k in user_courses]
        post_form.post_course.choices = post_courses

        if request.method == 'POST':
            title = post_form.title.data
            content = post_form.content.data
            post_course = post_form.post_course.data
            course = UserCourses.query.filter_by(course_id=post_course).first()
            post_course_name = course.course_name
            post_course_code = course.course_code
            print(course.course_code)

            if current_user.role == 'S':
                type = "Request"
            else:
                type = "Offer"
            author = current_user.username
            date_time = datetime.now()
            blog_post = StudentPost(title=title, author=author, date_posted=date_time, content=content,
                                type=type, post_course=post_course_name, post_course_code=post_course_code)

            db.session.add(blog_post)
            db.session.commit()

            return redirect(url_for('home'))

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"

        user_courses = TutorCourses.query.filter_by(user_id=this_user.id).all()
        post_courses = [(k.course_id, k.course_name) for k in user_courses]
        post_form.post_course.choices = post_courses
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

        if request.method == 'POST':
            title = post_form.title.data
            content = post_form.content.data
            post_course = post_form.post_course.data
            course = TutorCourses.query.filter_by(course_id=post_course).first()
            post_course_name = course.course_name
            post_course_code = course.course_code
            print(course.course_code)

            if current_user.role == 'S':
                type = "Request"
            else:
                type = "Offer"
            author = current_user.username
            date_time = datetime.now()
            blog_post = StudentPost(title=title, author=author, date_posted=date_time, content=content,
                                type=type, post_course=post_course_name, post_course_code=post_course_code)

            db.session.add(blog_post)
            db.session.commit()

            return redirect(url_for('home'))

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    return render_template('addNewStudentPost.html', username=current_user.username, post_form=post_form,
                           user_object=user_object, this_user=this_user, t_status=t_status, role_name=role_name)


# Community Forums Page - Search
@app.route('/forum_results')
def forum_search_results(search):
    this_user = User.query.filter_by(username=current_user.username).first()
    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    search_form = TutorSearchForm(request.form)

    results = []
    search_string = search.data['search']

    if search_string:
        if search.data['select'] == 'Course Code':
            qry = db.session.query(StudentPost).filter(StudentPost.post_course_code.contains(search_string)).order_by(StudentPost.date_posted.desc())

            results = qry.all()

        elif search.data['select'] == 'Course Name':
            qry = db.session.query(StudentPost).filter(StudentPost.post_course.contains(search_string)).order_by(StudentPost.date_posted.desc())

            results = qry.all()
        elif search.data['select'] == 'User Name':
            qry = db.session.query(StudentPost).filter(
                StudentPost.author.contains(search_string)).order_by(StudentPost.date_posted.desc())

            results = qry.all()
        else:
            qry = db.session.query(RoomPost)
            results = qry.all()
    else:
        qry = db.session.query(RoomPost)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/allstudentposts')
    else:
        # display results
        student_posts = results
        # table.border = True

        return render_template('studentPosts.html', this_user=this_user, student_posts=student_posts, role_name=role_name, t_status=t_status, search_form=search_form)


############################################################################################################
##
# PROFILE PAGES
##
############################################################################################################


# Edit User Email used in profile
@app.route('/editUserProfile', methods=['POST'])
def editUserProfile():
    user_edit = User.query.filter_by(id=request.form['id']).first()

    user_edit.email = request.form['email']

    db.session.commit()

    return jsonify({'result': 'success'})


# User Updates 'About Me' Profile Section
@app.route('/update_aboutme', methods=['POST', 'GET'])
def update_aboutme():

    user_object = User.query.filter_by(username=current_user.username).first()
    profile_me = user_object.about_me
    if request.method == 'POST':

        profile_me2 = request.form["about_me_profile"]
        print(profile_me2)
        new_aboutme = User.query.filter_by(username=current_user.username).update(dict(about_me=profile_me2))
        db.session.commit()

    return render_template('aboutMe.html', user_object=user_object, username=current_user.username)


# Personal Profile Page / Edit Your Profile Page
@app.route("/profile/", methods=['GET', 'POST'])
def profile():
    user_object = User.query.filter_by(username=current_user.username).first()
    this_user = User.query.filter_by(username=current_user.username).first()

    status = user_object.status
    role = user_object.role
    image_fp = user_object.user_photo
    about_me = user_object.about_me

    setdbstatus = status

    user_files = FileUpload.query.filter_by(username=current_user.username).all()

    # profile picture form
    image_form = ImageUploadForm()

    if image_form.validate_on_submit():
        image_filename = photos.save(request.files[image_form.image.name])
        user_object2 = User.query.filter_by(username=current_user.username).update(dict(user_photo=image_filename))
        db.session.commit()

        return redirect(url_for('profile'))

    t_status = "not sure"

    posts = RoomPost.query.filter_by(author=this_user.username).order_by(RoomPost.date_posted.desc()).all()
    student_posts = StudentPost.query.filter_by(author=this_user.username).order_by(StudentPost.date_posted.desc()).all()
    user_courses = UserCourses.query.filter_by(user_id=this_user.id).order_by(UserCourses.user_course_id.desc()).all()

    tutor_courses = TutorCourses.query.filter_by(user_id=this_user.id).order_by(TutorCourses.tutor_course_id.desc()).all()

    if role == "S":
        role_name = "Student"
        student_posts = StudentPost.query.filter_by(author=this_user.username).order_by(StudentPost.date_posted.desc()).all()

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif role == "T":
        role_name = "Tutor"
        posts = RoomPost.query.filter_by(author=this_user.username).order_by(RoomPost.date_posted.desc()).all()
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status


    elif role == "A":
        role_name = "Admin"

    room_posts = RoomPost.query.filter_by(author=current_user.username).order_by(RoomPost.date_posted.desc()).all()

    # user_files = FileUpload.query.filter_by(username=current_user.username).all()

    if status == 0:
        status_string = "Offine"
    elif status == 1:
        status_string = "Online"
    elif status == 2:
        status_string = "Busy"

    # file uploads
    file_form = FileUploadForm()

    if file_form.validate_on_submit():
        file = request.files[file_form.file.name]
        new_file = FileUpload(file_name=file.filename, username=current_user.username, data=file.read())
        db.session.add(new_file)
        db.session.commit()
        return redirect(url_for('profile'))

    # online status form
    ts_form = TutorStatus()

    #sets status default index based on userstatus
    ts_form.status.default = setdbstatus

    if ts_form.validate_on_submit():
        s1 = ts_form.status.data
        print(s1)

        if (s1 == '0'):
            setdbstatus = 0
            status_string = 'Offline'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()
        if (s1 == '1'):
            setdbstatus = 1
            status_string = 'Online'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()
        if (s1 == '2'):
            setdbstatus = 2
            status_string = 'Busy'
            db_status = User.query.filter_by(username=current_user.username).update(dict(status=setdbstatus))
            db.session.commit()

    return render_template('profile.html', username=current_user.username, image_fp=image_fp,
                           status_string=status_string, room_posts=room_posts, role_name=role_name, file_form=file_form,
                           user_files=user_files, image_form=image_form, user_object=user_object, this_user=this_user,
                           status=status, t_status=t_status, about_me=about_me, ts_form=ts_form, setdbstatus=setdbstatus, student_posts=student_posts, posts=posts, user_courses=user_courses, tutor_courses=tutor_courses)


# Download a User-Uploaded File on Profile Page
@app.route('/download/<string:dl_name>/')
def download(dl_name):
    # file_data = FileUpload.query.first()
    file_data = FileUpload.query.filter_by(file_name=dl_name).first()

    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)


# Public Profile Page - pub_profile.html
@app.route("/profile/<username>", methods=['GET', 'POST'])
def pub_profile(username):
    thisUser = current_user.username
    #public profile person
    user_object = User.query.filter_by(username=username).first()

    this_user = User.query.filter_by(username=current_user.username).first()
    this_role = this_user.role
    t_status = "not sure"

    user_courses = UserCourses.query.filter_by(user_id=user_object.id).order_by(UserCourses.user_course_id.desc()).all()

    if this_role == "S":
        student_posts = StudentPost.query.filter_by(author=username).order_by(StudentPost.date_posted.desc()).all()
        role_name = "Student"

    elif this_role == "T":
        posts = RoomPost.query.filter_by(author=username).order_by(RoomPost.date_posted.desc()).all()
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status
        user_courses = TutorCourses.query.filter_by(user_id=user_object.id).order_by(TutorCourses.tutor_course_id.desc()).all()
        role_name = "Tutor"

    elif this_role == "A":
        posts = RoomPost.query.filter_by(author=username).order_by(RoomPost.date_posted.desc()).all()
        t_status = "Admin"
        role_name = "Admin"

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
    pub_role = user_object.role
    about_me = user_object.about_me

    posts = RoomPost.query.filter_by(author=username, visible=True).order_by(RoomPost.date_posted.desc()).all()

    student_posts = StudentPost.query.filter_by(author=username).order_by(StudentPost.date_posted.desc()).all()

    if pub_role == "S":
        student_posts = StudentPost.query.filter_by(author=username).order_by(StudentPost.date_posted.desc()).all()
        pub_role_name = "Student"
    elif pub_role == "T":
        posts = RoomPost.query.filter_by(author=username).order_by(RoomPost.date_posted.desc()).all()
        pub_role_name = "Tutor"
    elif pub_role == "A":
        posts = RoomPost.query.filter_by(author=username).order_by(RoomPost.date_posted.desc()).all()
        pub_role_name = "Admin"

    if status == 0:
        status_string = "Offline"
    elif status == 1:
        status_string = "Online"
    elif status == 2:
        status_string = "Busy"

    return render_template('pub_profile.html', thisUser=thisUser, username=username, firstname=firstname,
                           lastname=lastname, email=email, status_string=status_string, posts=posts,
                           role_name=role_name, about_me=about_me, image_form=image_form, user_object=user_object, user_files=user_files,
                           this_user=this_user, student_posts=student_posts, user_courses=user_courses, pub_role_name=pub_role_name, t_status=t_status)


# Gets Profile Pics
@app.route('/uploads/pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


# Profile Page - Choose a Program
@app.route("/profile_programs", methods=['GET', 'POST'])
def profile_programs():

    this_user = User.query.filter_by(username=current_user.username).first()

    t_status = "not sure"

    available_programs = Program.query.all()

    program_list = [(k.program_id, k.programName) for k in available_programs]
    form1 = ProgramForm()

    form1.program_options.choices = program_list

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

        if request.method == 'POST':
            program_picked = form1.program_options.data
            this_program = Program.query.filter_by(program_id=program_picked).first()

            program_courses = ProgramCourse.query.filter_by(program_id=program_picked).all()

            return redirect(url_for('student_courses', program_id=program_picked))

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

        if request.method == 'POST':
            program_picked = form1.program_options.data
            this_program = Program.query.filter_by(program_id=program_picked).first()
            program_courses = ProgramCourse.query.filter_by(program_id=program_picked).all()

            return redirect(url_for('tutor_courses', program_id=program_picked))

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    return render_template('profilePrograms.html', username=current_user.username, this_user=this_user, form1=form1, role_name=role_name, t_status=t_status)


# Profile Page - Add Courses (student)
@app.route("/student_courses/<int:program_id>", methods=['GET', 'POST'])
def student_courses(program_id):

    this_user = User.query.filter_by(username=current_user.username).first()

    this_tutor = Tutor.query.filter_by(user_id=this_user.id).first()

    u_courses = UserCourses.query.filter_by(user_id=this_user.id).order_by(UserCourses.user_course_id.desc()).all()

    this_program = Program.query.filter_by(program_id=program_id).first()
    t_status = "not sure"

    if this_user.role == 'S':
        role_name = "Student"

        if Tutor.query.filter_by(user_id=this_user.id).first():
            tutor = Tutor.query.filter_by(user_id=this_user.id).first()
            t_status = tutor.tutor_status

    elif this_user.role == 'T':
        role_name = "Tutor"
        tutor = Tutor.query.filter_by(user_id=this_user.id).first()
        t_status = tutor.tutor_status

    elif this_user.role == 'A':
        role_name = "Admin"
        t_status = "Admin"

    # program = Program.query.filter_by(program_name=program_name).first()

    program_courses = ProgramCourse.query.filter_by(program_id=program_id).all()
    course_list = [(k.program_course_id, k.courseName) for k in program_courses]

    form = CourseForm()

    form.course_options.choices = course_list

    if request.method == 'GET':
        return render_template('studentCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)

    if request.method == 'POST':

        course_picked = form.course_options.data

        this_course = ProgramCourse.query.filter_by(program_course_id=course_picked).first()
        this_user = User.query.filter_by(username=current_user.username).first()
        user_course = UserCourses(user_id=this_user.id, course_name=this_course.courseName,
                                    course_id=this_course.program_course_id, course_code=this_course.courseCode)
        db.session.add(user_course)
        db.session.commit()

        return redirect(url_for('student_courses', program_id=program_id))

    return render_template('studentCourses.html', username=current_user.username, this_user=this_user, form=form, role_name=role_name, t_status=t_status, u_courses=u_courses, this_program=this_program)


# Profile Page - Deletes User Uploads
@app.route('/deleteUserFile', methods=['POST'])
def deleteUserFile():
    file = FileUpload.query.filter_by(username=current_user.username, file_name=request.form['id']).first()

    db.session.delete(file)
    db.session.commit()

    return jsonify({'result': 'success'})


# Profile Page - Deletes User Course
@app.route('/deleteUserCourse', methods=['POST'])
def deleteUserCourse():

    user = User.query.filter_by(username=current_user.username).first()
    user_id = user.id
    user_course = UserCourses.query.filter_by(user_id=user_id, user_course_id=request.form['id']).first()
    db.session.delete(user_course)
    db.session.commit()

    return jsonify({'result': 'success'})


######################################################
##
# PROGRAMS, COURSES, etc
##
######################################################


############################################################################################################
##
#  PRIVATE CHAT PAGE
##
############################################################################################################


# Private Chat Page
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
        newFile = RoomUpload(file_name=file.filename, room_name=roomName, username=current_user.username,
                             data=file.read())
        db.session.add(newFile)
        db.session.commit()
        return redirect(url_for('private_chat'))

    return render_template('private_chat.html', username=current_user.username, date_stamp=date_stamp,
                           roomName=roomName, message_object=message_object,
                           authorName=authorName, connected_stamp=connected_stamp, file_form=file_form,
                           room_files=room_files, room=room_object, this_user=this_user, role_name=role_name,
                           roomVisible=roomVisible)


# Private Chat Page - Download Files
@app.route('/download_room/<string:dl_name>/')
def room_download(dl_name):
    # file_data = FileUpload.query.first()ffd
    file_data = RoomUpload.query.filter_by(file_name=dl_name).first()

    return send_file(BytesIO(file_data.data), attachment_filename=file_data.file_name, as_attachment=True)


# Admin Portal - View Chat Log for Each Room
@app.route('/chat_log/<int:room_id>', methods=['GET', 'POST'])
def chat_log(room_id):
    if session["userRole"] != "A":
        return "You are not an authorized admin please go back"

    room = RoomPost.query.filter_by(id=room_id).first()

    this_user = User.query.filter_by(username=current_user.username).first()

    message_object = Message.query.filter_by(room=room.room_title).order_by(Message.id.desc()).all()

    return render_template('chat_log.html', room=room, username=current_user.username, this_user=this_user,
                           message_object=message_object)


# Admin Portal - Delete Chat Logs for Rooms
@app.route('/deleteLogs', methods=['POST'])
def deleteLogs():
    room = RoomPost.query.filter_by(id=request.form['id']).first()

    # delete all messages by room title
    db.session.query(Message).filter_by(room=room.room_title).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Admin Portal - delete Room Uploads for Rooms
@app.route('/deleteRoomUploads', methods=['POST'])
def deleteRoomUploads():
    room = RoomPost.query.filter_by(id=request.form['id']).first()

    db.session.query(RoomUpload).filter_by(room_name=room.room_title).delete()
    db.session.commit()

    return jsonify({'result': 'success'})


# Admin Portal - Update Room
@app.route('/updateRoom', methods=['POST'])
def updateRoom():
    room = RoomPost.query.filter_by(id=request.form['id']).first()

    room.room_title = request.form['title']
    room.content = request.form['content']
    # room.date_posted = date_time = datetime.now()
    room.date_posted = datetime.now()

    db.session.commit()

    return jsonify({'result': 'success', "room_title": room.room_title})



# Admin Portal - Update Room Profile?
@app.route('/updateRoomProfile', methods=['POST'])
def updateRoomProfile():
    room = RoomPost.query.filter_by(id=request.form['id']).first()

    room.title = request.form['name']
    room.room_title = request.form['title']
    room.content = request.form['content']
    # room.date_posted = date_time = datetime.now()
    room.date_posted = datetime.now()

    db.session.commit()

    return jsonify({'result': 'success'})


############################################################################################################
##
# PRIVATE CHAT - TUTOR CONTROLS
##
############################################################################################################


# makes room private used in chat and admin portal
@app.route('/privateRoom', methods=['POST'])
def privateRoom():
    room = RoomPost.query.filter_by(id=request.form['id']).first()
    room.visible = False
    db.session.commit()

    # sets rooms tutor status to busy
    room_tutor = User.query.filter_by(username=room.author).first()
    room_tutor.status = 2
    db.session.commit()

    return jsonify({'result': 'success', 'room_status': room.visible})


# makes room private used in chat and admin portal
@app.route('/publicRoom', methods=['POST'])
def publicRoom():
    room = RoomPost.query.filter_by(id=request.form['id']).first()
    room.visible = True
    db.session.commit()

    # sets rooms tutor status to online
    room_tutor = User.query.filter_by(username=room.author).first()
    room_tutor.status = 1
    db.session.commit()

    return jsonify({'result': 'success'})


############################################################################################################
##
# PRIVATE CHAT FUNCTIONS - private_chat.html
##
############################################################################################################


# when user sends message
@socketio.on('message')
def message(data):
    room = session.get('roomName')
    message_time = strftime('%I:%M%p %m-%d-%Y', localtime())
    message = Message(message=data['msg'], username=data['username'], room=data['room'], created_at=message_time)
    db.session.add(message)
    db.session.commit()

    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': strftime('%b-%d %I:%M%p', localtime())},
         room=data['room'])


# ran when joining room
@socketio.on('join')
def join(data):
    room = session.get('roomName')
    # join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been established')
    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])


# when uploading a file
@socketio.on('upload')
def upload(data):
    room = session.get('roomName')
    # join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' uploaded a file to ' + data['room'] + " room")
    send({'msg': data['username'] + " sent a file to the " + data['room'] + " room."}, room=data['room'])


# when tutor makes room private
@socketio.on('private')
def private(data):
    room = session.get('roomName')
    # join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' has now started a private session in room' + data['room'])
    send({'msg': "Tutor " + data['username'] + " has now made the " + data['room'] + " room private."},
         room=data['room'])


# when tutor makes room public
@socketio.on('public')
def public(data):
    room = session.get('roomName')
    # join_room(data['room'])
    join_room(room)
    # message_object = Message.query.filter_by(room='room').all()
    print(current_user.username + ' has now ended a private session in room' + data['room'])
    send({'msg': "Tutor " + data['username'] + " has now made the " + data['room'] + " room public."},
         room=data['room'])


# when user leaves room
@socketio.on('leave')
def leave(data):
    room = session.get('roomName')
    leave_room(room)
    # leave_room(data['room'])
    session['roomName'] = " "
    print('Connection on ' + data['room'] + ' with user ' + current_user.username + ' has been lost')
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])


# when tutor closes room
@socketio.on('close_room')
def close_room(data):
    # room = data['room']
    room = session.get('roomName')
    print('Tutor ' + current_user.username + ' has closed Room: ' + room + '.')


############################################################################################################
##
# ERROR PAGES
##
############################################################################################################

# 403 status explicitly
@app.errorhandler(403)
def forbidden(error):

    return render_template('403.html'), 403


# 404 status explicitly
@app.errorhandler(404)
def not_found(error):

    return render_template('404.html'), 404


# 405 status explicitly
@app.errorhandler(405)
def method_not_allowed(error):

    return render_template('405.html'), 405


# 500 status explicitly
@app.errorhandler(500)
def internal_server_error(error):

    return render_template('500.html'), 500


############################################################################################################
##
# MISC
##
############################################################################################################


## CHANGE ME AT DEPLOY
if __name__ == '__main__':
    socketio.run(app)
    # app.run()
    # ^ uncomment this when running and comment out socketio.run(app) at deployment
