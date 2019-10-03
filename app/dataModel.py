from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app import app


###     AUTHOR: AUSTIN PAUL
###     DATE: SEPT 26 2019
###     QUICKFIX_IO DIRTYBITS

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

class History(db.Model):
    """ History Model """

    __tablename__="history"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)

class Student(db.Model):

    __tablename__="student"

    student_id = db.Column(db.Integer, primary_key=True)
    about_me = db.Column(db.Text)
    school_id = db.Column(db.Integer)
    program_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

class Tutor(db.Model):

    __tablename__="tutor"

    tutor_id = db.Column(db.Integer, primary_key=True)
    about_tutor = db.Column(db.Text, nullable=False)
    credentials_file = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer)


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
    room = db.Column(db.String(25), nullable=False)
    created_at = db.Column(db.Text)

# data model for blogpost table recently added in heroku db
class RoomPost(db.Model):
    """ Blogpost Model"""

    __tablename__= "roompost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    room_title = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    type = db.Column(db.String(25))

# data model for blogpost table recently added in heroku db
class RoomComment(db.Model):
    """ Comment Model"""

    __tablename__= "commentpost"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer)
    comment_author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)