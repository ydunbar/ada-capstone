from dotenv import load_dotenv
from os import environ
load_dotenv('.env')

# Statement for enabling the development environment
# DEBUG = True
# Enable protection agains *Cross-site Request Forgery (CSRF)*
# CSRF_ENABLED = True

# Secret key for signing cookies
SECRET_KEY = environ.get('SECRET_KEY')

# Tokens etc
# GITHUB_CLIENT_ID = environ.get('GITHUB_CLIENT_ID')
# GITHUB_CLIENT_SECRET = environ.get('GITHUB_CLIENT_SECRET')

# Define the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

# base directory? maybe don't need if things aren't nested