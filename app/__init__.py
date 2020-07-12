from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# from flask.cli import with_appcontext

app = Flask(__name__)
app.secret_key = '99db118651486b4a10f8e4d33644f799'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# @with_appcontext
# def seed():
#     role1 = Role(name='mentor').save()
# def register_commands(app):
#     """Register CLI commands."""
#     app.cli.add_command(seed)
# register_commands(app)

from app import routes