from flask import Flask, redirect, url_for, session, request
from flask import render_template
from flask_oauth import OAuth
from models import User

SECRET_KEY = '123'
DEBUG = True
FACEBOOK_APP_ID = '1420298884864869'
FACEBOOK_APP_SECRET = 'f11b46f7a016760722b968de867d7432'


app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

def get_context():
    data = session.get('data')
    if data:
        user = User.get_or_create(email=data['email'])
        invite_groups = user.get_invite_groups()

        if 'work' in data:
            employer = data['work'][0]['employer']['name']
            position = data['work'][0]['position']['name']
        else:
            employer = user.employer
            position = user.position

        if 'location' in data:
            location = data['location']['name']
        else:
            location = user.location

        return {
            'user': user,
            'email': user.email or data['email'],
            'name': user.name or data['name'],
            'employer': employer,
            'position': position,
            'location': location,
            'bio': user.bio,
            'data': data,
            'photo_url': 'https://graph.facebook.com/%s/picture' % data['id'],
        }
    return {}


@app.route("/profile", methods=['POST', 'GET'])
def profile():
    context = get_context()
    context.update(dict(success=False))
    if request.method == 'POST':
        user = User.get_or_create(email=context['email'])
        user.employer = request.form['employer']
        user.position = request.form['position']
        user.location = request.form['location']
        user.bio = request.form['bio']
        user.save()
        context = get_context()
        context.update(dict(success=True))
        print request.form
    return render_template('profile.html', **context)

@app.route("/create", methods=['POST', 'GET'])
def create():
    context = get_context()
    context.update(dict(success=False))
    user = User.get_or_create(email=context['email'])
    all_users = User.get_all(exclude_user_id=user.id)
    context.update({'all_users': list(all_users)})
    if request.method == 'POST':
        context.update(dict(success=True))
    return render_template('create.html', **context)

@app.route("/receipt", methods=['POST', 'GET'])
def receipt():
    context = get_context()
    context.update(dict(success=False))
    return render_template('receipt.html', **context)


@app.route("/loans", methods=['POST', 'GET'])
def loans():
    context = get_context()
    return render_template('loans.html', **context)


@app.route("/requests", methods=['POST', 'GET'])
def requests():
    context = get_context()
    return render_template('requests.html', **context)

@app.route("/")
def index():
    context = get_context()
    return render_template('index.html', **context)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)
    session.pop('data', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)

    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')
    data = facebook.get('/me').data
    session['data'] = data
    User.get_or_create(
        email=data['email'],
        name=data['name'],
        facebook_id=data['id'],
    )
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
