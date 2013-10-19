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
        return {
            'email': data['email'],
            'name': data['name'],
            'photo_url': 'https://graph.facebook.com/%s/picture' % data['id'],
        }
    return {}


@app.route("/loan", methods=['POST', 'GET'])
def loan_form():
    context = get_context()
    print request.form
    if request.method == 'POST':
        loan_amount = request.form['loan_amount']
        user = User.get_or_create(email=context['email'])
        user.loan_amount = loan_amount
        user.save()
        return redirect(url_for('index'))
    return render_template('loan_form.html', **context)

@app.route("/")
def index():
    context = get_context()
    if context:
        user = User.get_or_create(email=context['email'])
        if not user.loan_amount:
            return redirect(url_for('loan_form'))

        all_users = User.get_all(exclude_user_id=user.id)
        context.update({'all_users': list(all_users)})
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
    print 'here', next_url
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

    return redirect(next_url)

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
