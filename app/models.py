from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

role_user = db.Table('role-user', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    image = db.Column(db.String(), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys = 'Post.author_id')
    recieved_posts = db.relationship('Post', backref='recipient', lazy=True, foreign_keys = 'Post.recipient_id')
    roles = db.relationship('Role', secondary=role_user, backref='users', lazy='dynamic')
    # lazy='dynamic' => query object instead of collection, for querying related objects

    # skills; full-stack, front-end, back-end

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), unique=True, nullable=False)
    # users psuedo column

    # seed data; refactor in loop? 
    # Why does structure in terminal look different?
    @staticmethod
    def generate_roles(): 
        role1 = Role(name='mentor', description='provide mentorship')
        role2 = Role(name='mentee', description='recieve mentorship')
        role3 = Role(name='collaborator', description='collaborate on projects')
        db.session.add(role1)
        db.session.add(role2)
        db.session.add(role3)
        db.session.commit()
        # <Role (transient 4550179040)>