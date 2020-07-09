import os
import secrets
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    # change to posts addressed to user
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/matches', methods=['GET'])
@login_required
def matches():
    return render_template('matches.html')

@app.route('/browse', methods=['GET'])
def browse():
    users = User.query.all()
    return render_template('browse.html', users=users)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_filename)
    form_picture.save(picture_path)
    return picture_filename

@app.route('/profile/<username>', methods=['GET', 'POST'])
# @login_required
def profile(username):
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
        db.session.commit()
        flash('Account has been updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pictures/' + 'current_user.image')
    # placeholder posts
    return render_template('profile.html', image_file=image_file, form=form)

# add route for user profiles

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
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