import os
import secrets
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, SearchForm
from app.models import User, Post, Role, Skill
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    # only if logged in:
    if current_user.is_authenticated:
        posts = Post.query.filter_by(recipient=current_user)
    else:
        posts = []        
    return render_template('home.html', posts=posts)

@app.route('/matches', methods=['GET'])
@login_required
def matches():   
    # TODO: add logic for matches based on complementary roles
    # if current_user.roles includes mentor
        # if role includes full-stack
            # get users with mentee:full stack role
    matches = User.query.all()
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
        user_matches = []
        role = form.role.data
        skill = form.skill.data
        for user in all_users:
            # get user's matching roles
            role_matches = user.roles.filter_by(name=role).all()
            # search user's matching roles for matching skill
            for role in role_matches:
                skill_match = role.skills.filter_by(name=skill).first()
                if skill_match:
                    user_matches.append(user)
        users = user_matches
    elif request.method == 'GET':
        users = User.query.all()
    return render_template('browse.html', users=users, form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_filename)
    form_picture.save(picture_path)
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
            old_pic = current_user.image_file
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
            if old_pic != 'default.jpg':
                os.remove(os.path.join(app.root_path, 'static/profile_pics', old_pic))
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
       
    image_file = url_for('static', filename='profile_pictures/' + 'current_user.image')
    return render_template('profile_settings.html', image_file=image_file, form=form)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        image_file = url_for('static', filename='profile_pictures/' + 'user.image')
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
        flash('Post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

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