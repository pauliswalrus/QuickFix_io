from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError, Email

from passlib.hash import pbkdf2_sha256
from app.sqlalq_datamodels import User, FileUpload


###     AUTHOR: AUSTIN PAUL
###     DATE: OCT 4
###     QUICKFIX_IO DIRTYBITS
###     PRE-SPRINT 4 TURNIN OCT 4 BUILD


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
    submit_button = SubmitField('Submit')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a new username")


class TutorForm(FlaskForm):
    """ TutorRegistration form """

    about_tutor = TextAreaField('about_label', validators=[InputRequired(message="Post required")])
    credentials_file = FileField('file_upload', validators=[InputRequired(message="Select a file")])
    submit_button = SubmitField('Create Account')

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
    """ RoomPost Form """

    # type = SelectField('type_label', choices=[('Request', 'Request'), ('Offer', 'Offer')])
    title = StringField('title_label', validators=[InputRequired(message="Title required"), Length(min=4, max=50, message="Title must be between 4 and 50 characters")])
    subtitle = StringField('subtitle_label', validators=[InputRequired(message="Room required"), Length(min=4, max=50, message="Room Name must be between 4 and 50 characters")])
    content = TextAreaField('content_label', validators=[InputRequired(message="Post required")])
    submit_button = SubmitField('Add Post')

class CommentForm(FlaskForm):
    """ RoomPost Form """

    # type = SelectField('type_label', choices=[('Request', 'Request'), ('Offer', 'Offer')])
    content = TextAreaField('content_label', validators=[InputRequired(message="Post required")])
    submit_button = SubmitField('Add Comment')


class FileUploadForm(FlaskForm):
    """ file upload """

    file = FileField('file_upload', validators=[InputRequired(message="Select a file")])
    submit_button = SubmitField('Add New File')

class ImageUploadForm(FlaskForm):
    """ file upload """

    image = FileField('image_upload', validators=[InputRequired(message="Select an image")])
    submit_button1 = SubmitField('Add New Image')

class RoomJoin(FlaskForm):
    """ Room Create """

    room_private = StringField('Private Room')
    submit_button2 = SubmitField('Begin Private Chat')

class TutorStatus(FlaskForm):
    """ Status"""

    status = SelectField('Status', choices=[('0', 'Offline'), ('1', 'Online')])
    submit_button3 = SubmitField('Change Status')

