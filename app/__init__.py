from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.secret_key = '99db118651486b4a10f8e4d33644f799'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# # Engine for connecting to db.
# engine = create_engine('sqlite:///site.db')

# # create a configured "Session" class
# Session = sessionmaker(bind=engine)

# # create a Session
# session = Session(bind=engine, autoflush=False)

from app import routes