from flask import Flask, render_template, url_for
app = Flask(__name__)

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
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/matches')
def matches():
    return render_template('matches.html')

@app.route('/browse')
def browse():
    return render_template('browse.html')

@app.route('/profile')
def profile():
    return render_template('profile.html', posts=posts)

# run without env vars
if __name__ == '__main__':
    app.run(debug=True)