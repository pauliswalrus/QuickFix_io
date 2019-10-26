from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from __init__ import app


###     AUTHOR: AUSTIN PAUL
###     DATE: OCT 25
###     QUICKFIX_IO DIRTYBITS
###     SPRINT 6 OCT 25 BUILD DEPLOYED AT
###     quickfix-io.herokuapp.com

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    """ User Model """

    __tablename__ = "users_new"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    firstname = db.Column(db.String(25), nullable=False)
    lastname = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(25), nullable=False)
    password = db.Column(db.String(), nullable=False)
    status = db.Column(db.Integer(), default=0)
    role = db.Column(db.Text, default="S")
    user_photo = db.Column(db.Text)

class Student(db.Model):

    __tablename__="student"

    student_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer)
    program_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

class Tutor(db.Model):

    __tablename__="tutor"

    tutor_id = db.Column(db.Integer, primary_key=True)
    about_tutor = db.Column(db.Text, nullable=False)
    credentials_file_data = db.Column(db.LargeBinary, nullable=False)
    credentials_file_name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users_new.id'))
    tutor_status = db.Column(db.String(25))
    application_comments = db.Column(db.Text)


class FileUpload(db.Model):

    __tablename__="file_uploads"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    file_name = db.Column(db.Text, nullable=False)
    data = db.Column(db.LargeBinary)

class RoomUpload(db.Model):

    __tablename__="room_uploads"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    file_name = db.Column(db.Text, nullable=False)
    room_name = db.Column(db.String(50), nullable=False)
    data = db.Column(db.LargeBinary)


class Message(db.Model):
    """ Message Model """

    __tablename__= "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    username = db.Column(db.String(25), nullable=False)
    room = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.Text)

# data model for blogpost table recently added in heroku db
class RoomPost(db.Model):
    """ Blogpost Model"""

    __tablename__= "roompost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    room_title = db.Column(db.String(50), unique=True, nullable=False)
    author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    type = db.Column(db.String(25))
    visible = db.Column(db.Boolean)

# data model for blogpost table recently added in heroku db
class RoomComment(db.Model):
    """Room Comment Model"""

    __tablename__= "commentpost"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer)
    comment_author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)


# data model for blogpost table recently added in heroku db
class StudentPost(db.Model):
    """ Blogpost Model"""

    __tablename__= "studentpost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    type = db.Column(db.String(25))

# data model for blogpost table recently added in heroku db
class PostComment(db.Model):
    """Student Post Comment Model"""

    __tablename__= "commentstudent"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    comment_author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

class Program(db.Model):
    """Program Model"""

    __tablename__ = "program"
    program_id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.Text)

class Course(db.Model):
    """Course Model"""

    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Text)
    program_id = db.Column(db.Integer, db.ForeignKey('program.program_id'))

    def __repr__(self):
        return '[Course {}]'.format(self.course_name)

def choice_query():
    return Course.query
