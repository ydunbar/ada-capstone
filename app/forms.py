from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    email = StringField('Email', validators=[DataRequired(message="email required")])
    password = PasswordField('Password', validators=[DataRequired(message="password required")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message="password required"), EqualTo('password', message="passwords must match")])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already associated with an account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    email = StringField('Email', validators=[DataRequired(message="email required")])  
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username taken')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already associated with an account')

class PostForm(FlaskForm):
    title = StringField('Title')
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')