from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.secret_key = '99db118651486b4a10f8e4d33644f799'

# placeholder posts
posts = [
    {
        'subject': 'question',
        'message': 'have any tips?'
    },
    {
        'subject': 'hello',
        'message': 'nice to meet you!'
    },
]

@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/matches', methods=['GET'])
def matches():
    return render_template('matches.html')

@app.route('/browse', methods=['GET'])
def browse():
    return render_template('browse.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # placeholder posts
    return render_template('profile.html', posts=posts)

# add route for user profiles

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@site.com' and form.password.data == 'password':
            flash('Success!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Failed', 'danger')
    return render_template('login.html', form=form)

# run without env vars
if __name__ == '__main__':
    app.run(debug=True)