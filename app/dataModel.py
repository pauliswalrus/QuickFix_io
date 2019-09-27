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

class History(db.Model):
    """ History Model """

    __tablename__="history"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)

class Message(db.Model):
    """ Message Model """

    __tablename__= "messages"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    username = db.Column(db.String(25), nullable=False)
    room = db.Column(db.String(25), nullable=False)

# data model for blogpost table recently added in heroku db
class BlogPost(db.Model):
    """ Blogpost Model"""

    __tablename__= "blogpost"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    subtitle = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(25), nullable=False)
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)
    type = db.Column(db.String(25))