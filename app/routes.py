# followed resource for Flask-Dance Google OAuth: https://github.com/singingwolfboy/flask-dance-google-sqla/blob/master/app/oauth.py
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, SearchForm
from app.models import User, Post, Role, Skill, OAuth
from flask_login import login_user, current_user, logout_user, login_required
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc import NoResultFound

# TODO: move dotenv references to config file
from dotenv import load_dotenv
from os import environ
load_dotenv('.env')

GITHUB_OAUTH_CLIENT_ID = environ.get('GITHUB_OAUTH_CLIENT_ID')
GITHUB_OAUTH_CLIENT_SECRET = environ.get('GITHUB_OAUTH_CLIENT_SECRET')
github_blueprint = make_github_blueprint(client_id=GITHUB_OAUTH_CLIENT_ID, client_secret=GITHUB_OAUTH_CLIENT_SECRET)
app.register_blueprint(github_blueprint, url_prefix='/github_login')
github_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user, user_required=False)

GOOGLE_OAUTH_CLIENT_ID = environ.get('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_OAUTH_CLIENT_SECRET = environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
google_blueprint = make_google_blueprint(client_id=GOOGLE_OAUTH_CLIENT_ID, client_secret=GOOGLE_OAUTH_CLIENT_SECRET, scope=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"])
app.register_blueprint(google_blueprint, url_prefix='/google_login')
google_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)

@app.route('/github')
def github_login():
    # if not github.authorized:
    return redirect(url_for('github.login'))

    resp = github.get('/user')
    info = resp.json()
    # flash('Request failed', 'danger')

# signal
@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    resp = blueprint.session.get('/user')

    if resp.ok:
        info = resp.json()
        username = info['login']
        email = info['email']
        avatar_url = info['avatar_url']
        query = User.query.filter_by(username=username)
        try:
            user = query.one() # .one() should only be used if getting only one result is mandatory for the rest of the method
        except NoResultFound:
            user = User(username=username, email=email, image=avatar_url)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        flash('You are logged in as {}'.format(info['login']), 'success')

@app.route('/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))

    resp = google.get('/oauth2/v1/userinfo')
    info = resp.json() # account_info returns name, email, picture
    # flash('Request failed', 'danger')

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    resp = blueprint.session.get('/oauth2/v1/userinfo')
    info = resp.json()
    user_id = info['id']

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(provider=google_blueprint.name, user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(provider=google_blueprint.name, user_id=user_id, token=token)

    if oauth.user:
        login_user(oauth.user)
        flash('You are logged in as {}'.format(info['name']), 'success')

    else:
        user = User(username=info['name'], email=info['email'], image=info['picture'])
        # Associate the new local user account with the OAuth token
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash('You are logged in as {}'.format(info['name']), 'success')

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    # only if logged in:
    if current_user.is_authenticated:
        posts = Post.query.filter_by(recipient=current_user)
    else:
        posts = []        
    return render_template('home.html', posts=posts)

def get_mentees(skill):
    all_users = User.query.all()
    all_users.remove(current_user)
    for user in all_users:
        role_match = user.roles.filter_by(name='mentee').first()
        if role_match:
            skill_match = role_match.skills.filter_by(name=skill).first()
            if skill_match:
                return user

def get_mentors(skill):
    all_users = User.query.all()
    all_users.remove(current_user)
    for user in all_users:
        role_match = user.roles.filter_by(name='mentor').first()
        if role_match:
            skill_match = role_match.skills.filter_by(name=skill).first()
            if skill_match:
                return user

# def unique_match(matches, user):
#     unique = True
#     for match in matches:
#         if match == user:
#             unique = False
#     return unique

@app.route('/matches', methods=['GET'])
@login_required
def matches():   
    # TODO: add logic for matches based on complementary roles
    matches = []
    roles = current_user.roles
    for role in roles:
        # if mentor
        if role.name == 'mentor':
            skills = role.skills
            for skill in skills:
                # if mentor: full-stack
                if skill.name == 'full-stack':
                    user = get_mentees('full-stack')
                    # TODO: check if user is already in matches
                    # if unique_match(matches, user): # not working,
                    # might just do a user filter_by().first() on matches
                    matches.append(user)
                # if mentor: back-end
                if skill.name == 'back-end':
                    user = get_mentees('back-end')
                    matches.append(user)
                    # if unique_match(matches, user):
                    matches.append(user)
                # if mentor: front-end
                if skill.name == 'front-end':
                    user = get_mentees('front-end')
                    matches.append(user)
                    # if unique_match(matches, user):
                    matches.append(user)
        # if mentee
        if role.name == 'mentee':
            skills = role.skills
            for skill in skills:
                if skill.name == 'full-stack':
                    user = get_mentors('full-stack')
                    # TODO: check if user is already in matches
                    # if unique_match(matches, user): # not working,
                    # might just do a user filter_by().first() on matches
                    matches.append(user)
                # if mentor: back-end
                if skill.name == 'back-end':
                    user = get_mentors('back-end')
                    matches.append(user)
                    # if unique_match(matches, user):
                    matches.append(user)
                # if mentor: front-end
                if skill.name == 'front-end':
                    user = get_mentors('front-end')
                    matches.append(user)
                    # if unique_match(matches, user):
                    matches.append(user)
        # if collaborator
        if role.name == 'mentee':
            skills = role.skills
            for skill in skills:
                # if collaborator: full-stack; show all users
                if skill.name == 'full-stack':
                    all_users = User.query.all()
                    all_users.remove(current_user)
                    matches = all_users
                # if collaborator: back-end; show all collaborators except back-end
                if skill.name == 'back-end':
                    all_users = User.query.all()
                    all_users.remove(current_user)
                    # TODO remove back-end
                    matches = all_users
                # if collaborator: front-end; show all collaborators except front-end
                if skill.name == 'front-end':
                    all_users = User.query.all()
                    all_users.remove(current_user)
                    # TODO remove front-end
                    matches = all_users
    return render_template('matches.html', matches=matches)

# with all users and search; should be one route or two (with search template extending browse?)?
@app.route('/browse', methods=['GET', 'POST'])
def browse():
    form = SearchForm()
    # refactor to create tuples from each skill.name
    form.skill.choices = [('full-stack', 'full-stack'), ('back-end', 'back-end'), ('front-end', 'front-end')]
    if request.method == 'POST':
        # TODO: make role and skill selection required. default to empty choice
        all_users = User.query.all()
        if current_user.is_authenticated:
            all_users.remove(current_user)
        user_matches = []
        role = form.role.data
        skill = form.skill.data
        for user in all_users:
            # get user's matching roles
            role_match = user.roles.filter_by(name=role).first()
            # search user's matching roles for matching skill
            if role_match:
                skill_match = role_match.skills.filter_by(name=skill).first()
                if skill_match:
                    user_matches.append(user)
        users = user_matches
    elif request.method == 'GET':
        users = User.query.all()
        if current_user.is_authenticated:
            users.remove(current_user)
    return render_template('browse.html', users=users, form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pictures', picture_filename)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_filename

def add_role(role_name, skill_name):
    roles = current_user.roles
    if roles.filter_by(name = role_name).first():
        role = roles.filter_by(name = role_name).first()
    else:
        role = Role(name=role_name, user_id=current_user.id)
    role.skills.append(Skill.query.filter_by(name = skill_name).first())
    db.session.add(role)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            # not showing picture
            # old_pic = current_user.image
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
            # delete old pic
            # if old_pic != 'default.jpg':
            #     os.remove(os.path.join(app.root_path, 'static', 'profile_pictures', old_pic))
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        # update role from checkboxes
        # TODO: delete roles
        # TODO: refactor skill checkboxes into selectmultiple field/DRY
        # TODO: make form remember checked boxes
        if form.mentor_fullstack.data:
            role = add_role('mentor', 'full-stack')
        if form.mentor_backend.data:
            role = add_role('mentor', 'back-end')
        if form.mentor_frontend.data:
            role = add_role('mentor', 'front-end')
        # else:
        #     current_user.roles.remove(current_user.roles.filter_by(name = 'mentor').first()) # works in db  
        if form.mentee_fullstack.data:
           role = add_role('mentee', 'full-stack')
        if form.mentee_backend.data:
            role = add_role('mentee', 'back-end')
        if form.mentee_frontend.data:
            role = add_role('mentee', 'front-end')
        if form.collaborator_fullstack.data:
            role = add_role('collaborator', 'full-stack')
        if form.collaborator_backend.data:
            role = add_role('collaborator', 'back-end')
        if form.collaborator_frontend.data:
            role = add_role('collaborator', 'front-end')
        db.session.commit()
        flash('Account has been updated', 'success')
        return redirect(url_for('profile_settings'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        # show checked roles
        form.mentor.data = current_user.roles.filter_by(name='mentor').first()
        form.mentee.data = current_user.roles.filter_by(name='mentee').first()
        form.collaborator.data = current_user.roles.filter_by(name='collaborator').first()
       
    image_file = url_for('static', filename='profile_pictures/' + current_user.image)
    return render_template('profile_settings.html', image_file=image_file, form=form)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        image_file = url_for('static', filename='profile_pictures/' + user.image)
        return render_template('profile.html', image_file=image_file, user=user)
    else:
        flash('User does not exist', 'danger')
        return redirect(url_for('home'))

@app.route('/post/<username>', methods=['GET', 'POST'])
@login_required
def new_post(username):
    user = User.query.filter_by(username=username).first()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, recipient=user)
        db.session.add(post)
        db.session.commit()
        flash('Message has been sent', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', title=post.title, post=post, legend='New Post')

@app.route('/post/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403) # forbidden route
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your message has been updated', 'success')
        return redirect(url_for('post', id=id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', form=form, legend='Update Post')

@app.route('/post/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.author != current_user:
        abort(403) # forbidden route
    db.session.delete(post)
    db.session.commit()
    flash('Your message has been deleted', 'success')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # next not working
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Failed', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))