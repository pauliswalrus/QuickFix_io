from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Email

from passlib.hash import pbkdf2_sha256
from dataModel import User

def invalid_credentials(form, field):
    """ Username and password checker"""

    username_entered = form.username.data
    password_entered = field.data

    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("Username or password is incorrect")
    #elif password_entered != user_object.password:
     #   raise ValidationError("Username or password is incorrect")


class RegistrationForm(FlaskForm):
    """ Registration form """

    username = StringField('username_label', validators=[InputRequired(message="Username required"), Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    firstname = StringField('firstname_label', validators=[InputRequired(message="First name required"), Length(min=4, max=25, message="First name must be between 4 and 25 characters")])
    lastname = StringField('lastname_label', validators=[InputRequired(message="Last name required"), Length(min=4, max=25, message="Last name must be between 4 and 25 characters")])
    email = StringField("email_label", validators=[InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label', validators=[InputRequired(message="Password required"), EqualTo('password', message="Passwords must match")])
    submit_button = SubmitField('Create Account')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a new username")


#just placeholders for forms, not currently used
class TutorRegistrationForm(FlaskForm):
    """ TutorRegistration form """

    username = StringField('username_label', validators=[InputRequired(message="Username required"), Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    firstname = StringField('firstname_label', validators=[InputRequired(message="First name required"), Length(min=4, max=25, message="First name must be between 4 and 25 characters")])
    lastname = StringField('lastname_label', validators=[InputRequired(message="Last name required"), Length(min=4, max=25, message="Last name must be between 4 and 25 characters")])
    email = StringField("email_label", validators=[InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    workplace = StringField('workplace_label', validators=[InputRequired("Please enter your workplace."), Length(min=4, max=25, message="Workplace must be between 4 and 25 characters")])
    occupation = StringField('occupation_label', validators=[InputRequired("Please enter your occupation."), Length(min=4, max=25, message="Occupation must be between 4 and 25 characters")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label', validators=[InputRequired(message="Password required"), EqualTo('password', message="Passwords must match")])
    submit_button = SubmitField('Create Account')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a new username")

##see above
class StudentRegistrationForm(FlaskForm):
    """ StudentRegistration form """

    username = StringField('username_label', validators=[InputRequired(message="Username required"), Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    firstname = StringField('firstname_label', validators=[InputRequired(message="First name required"), Length(min=4, max=25, message="First name must be between 4 and 25 characters")])
    lastname = StringField('lastname_label', validators=[InputRequired(message="Last name required"), Length(min=4, max=25, message="Last name must be between 4 and 25 characters")])
    email = StringField("email_label", validators=[InputRequired("Please enter your email address."), Email("This field requires a valid email address")])
    introduction = StringField('intro_label', validators=[InputRequired("Please enter your introduction."), Length(min=4, max=25, message="Intro must be between 4 and 25 characters")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    confirm_pswd = PasswordField('confirm_pswd_label', validators=[InputRequired(message="Password required"), EqualTo('password', message="Passwords must match")])
    submit_button = SubmitField('Create Account')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a new username")


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('username_label', validators=[InputRequired(message="Username required")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), invalid_credentials])
    submit_button = SubmitField('Login')


class RoomCreate(FlaskForm):
    """ Room Create """

    room_made = StringField('Private Room ', validators=[InputRequired(message="Must enter a room name")])
    submit_button = SubmitField('Room')

class BlogPostForm(FlaskForm):
    """ BlogPost Form """

    title = StringField('title_label', validators=[InputRequired(message="Title required")])
    subtitle = StringField('subtitle_label', validators=[InputRequired(message="Subtitle required")])
    content = TextAreaField('content_label', validators=[InputRequired(message="Post required")])
    submit_button = SubmitField('Add Post')