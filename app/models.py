from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# many Roles to many Skills
skill_role = db.Table('skill-role', 
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'))
)

# each User has many sent and recieved Posts, each User can have many Roles
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    image = db.Column(db.String(), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True, foreign_keys = 'Post.author_id')
    recieved_posts = db.relationship('Post', backref='recipient', lazy=True, foreign_keys = 'Post.recipient_id')
    roles = db.relationship('Role', backref='user', lazy='dynamic', foreign_keys = 'Role.user_id')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image}')"

# each Post has one author and one recipient
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), unique=True, nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

# each Role can have many Skills; each role belongs to one User
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(), unique=True, nullable=False)
    # description = db.Column(db.String(), unique=True, nullable=False)
    skills = db.relationship('Skill', secondary=skill_role, backref='role', lazy='dynamic')

# each Skill can belong to many Roles
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    # role psuedo column

    @staticmethod
    def generate_skills():
        skill1 = Skill(name='full-stack')
        skill2 = Skill(name='back-end')
        skill3 = Skill(name='front-end')
        db.session.add(skill1)
        db.session.add(skill2)
        db.session.add(skill3)
        db.session.commit()