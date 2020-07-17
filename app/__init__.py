# followed tutorial on file structure: https://www.digitalocean.com/community/tutorials/how-to-structure-large-flask-applications
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object
db = SQLAlchemy(app)
# moved to config:
# app.secret_key = '99db118651486b4a10f8e4d33644f799'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# app.run(debug=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from app import routes