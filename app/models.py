from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    image = db.Column(db.String(), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    # posts = db.relationship('Post', backref='author', lazy=True)

    # recieved_posts = db.relationship('Post', backref='recipient', lazy=True) 
    # sqlalchemy.exc.AmbiguousForeignKeysError: Can't determine join between 'user' and 'post'; tables have more than one foreign key constraint relationship between them. Please specify the 'onclause' of this join explicitly.
    # sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join condition between parent/child tables on relationship User.posts - there are multiple foreign key paths linking the tables.  Specify the 'foreign_keys' argument, providing a list of those columns which should be counted as containing a foreign key reference to the parent table.

    # create join table for "inbox"? User has one inbox which has many posts
    # inbox = db.relationship('Inbox', backref='user', lazy=True)

    # type; mentor/mentee
    # skills; full-stack, front-end, back-end

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    author = db.relationship('User', foreign_keys='Post.author_id')

    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.relationship('User', foreign_keys='Post.recipient_id')


    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

# class Inbox(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     posts = db.relationship('Post', backref='inbox', lazy=True)