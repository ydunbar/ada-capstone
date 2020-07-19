from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField, SelectField, widgets
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User, Role

# def role_query():
#     role_choices = []
#     roles = Role.query.all()
#     for role in roles:
#         role_choices.append(role.description)
#     return role_choices

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
    # role_choices = role_query()
    username = StringField('Username', validators=[DataRequired(message="Username required")])
    email = StringField('Email', validators=[DataRequired(message="email required")])  
    picture = FileField('Update profile picture', validators=[FileAllowed(['jpg', 'png'])])

    mentor = BooleanField('mentor')
    mentor_fullstack = BooleanField('full-stack')
    mentor_backend = BooleanField('back-end')
    mentor_frontend = BooleanField('front-end')

    mentee = BooleanField('mentee')
    mentee_fullstack = BooleanField('full-stack')
    mentee_backend = BooleanField('back-end')
    mentee_frontend = BooleanField('front-end')

    collaborator = BooleanField('collaborator')
    collaborator_fullstack = BooleanField('full-stack')
    collaborator_backend = BooleanField('back-end')
    collaborator_frontend = BooleanField('front-end')
    
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
    title = StringField('Subject', validators=[DataRequired()])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    role = SelectField('role', choices=[('mentor', 'mentor'), ('mentee', 'mentee'), ('collaborator', 'collaborator')])
    skill = SelectField('specialty', choices=[])
    submit = SubmitField('Search')