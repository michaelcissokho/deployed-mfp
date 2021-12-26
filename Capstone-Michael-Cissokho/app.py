from flask import Flask, render_template, jsonify, request, session, g, redirect, flash
from sqlalchemy import exc
from flask_bcrypt import Bcrypt
from forms import TickerLookup, SignupForm, LoginForm, MessageForm, EditProfileForm
from models import db, connect_db, User, Message
from constants import secret_key, api_key_secret, database, marketauxAPIKey
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database

bcrypt = Bcrypt()
connect_db(app)
db.create_all()

api_key = api_key_secret
link = 'https://financialmodelingprep.com/api/v3'


def send_return_data(data_from_api):
    # creating dict to retrieve all information from api and convert into internal dictionary
    return_data = dict()

    # send jsonify'd data back to "[somethhing-statement]Data" function in script.js
    for key, value in data_from_api.items():
        return_data[key] = value

    return jsonify(return_data)

##########################################################
# ticker data routes

@app.route('/ticker')
def get_ticker_data():
    # used to call index.html file

    return render_template('/users/ticker.html')

@app.route('/profile-data', methods=['POST'])
def get_profile_data():
    ticker = request.json.get('ticker').upper()

    # route will call financialmodelingprep.com API, I preset the params in advance because of errors connecting backend to front
    res = requests.get(f'{link}/profile/{ticker}?apikey={api_key}')

    data = res.json()[0]

    return send_return_data(data)

@app.route('/historical-price-data', methods=['POST'])
def get_historical_data():
    ticker = request.json.get('ticker').upper()

    res = requests.get(
        f'{link}/historical-price-full/{ticker}?apikey={api_key}')

    data = res.json()

    return send_return_data(data)

def getStatement(file):
    limit = request.json.get('limit')
    ticker = request.json.get('ticker').upper()
    
    res = requests.get(
        f'{link}/{file}/{ticker}?limit={limit}&apikey={api_key}')
    
    data = res.json()[0]

    return send_return_data(data)


@app.route('/income-statement-data', methods=['POST'])
def get_income_statement():

    return getStatement('income-statement')


@app.route('/balance-sheet-statement-data', methods=['POST'])
def get_balance_sheet():

    return getStatement('balance-sheet-statement')


@app.route('/cash-flow-statement-data', methods=['POST'])
def get_cash_flow_statement():

    return getStatement('cash-flow-statement')


##########################################
# homepage data routes
@app.route('/')
def homepage():

    return render_template('/users/home.html')

@app.route('/market-news', methods=['POST'])
def get_market_news():

    res = requests.get(f'https://api.marketaux.com/v1/news/all?countries=us&language=en&limit=3&api_token={marketauxAPIKey}')

    data = res.json()['data']

    return jsonify(data)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    print('****************************')
    print(session)
    print('****************************')


def checkForUser(route):
    if session.get('user-id') is None:
        flash('Access unauthorized', 'danger')
        return redirect(route)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if session.get('user-id'):
        del session['user-id']
    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data
            )
            db.session.commit()

        except exc.IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('/users/signup.html', form=form)

        session['user-id'] = user.id

        return redirect("/")

    else:
        return render_template('/users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            session['user-id'] = user.id
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    if session.get('user-id') is not None:
        del session['user-id']

    flash("You have successfully logged out.", 'success')
    return redirect("/users/login")

##############################################################################
# General user routes:


@app.route('/users/<int:user_id>')
def show_profile(user_id):
    checkForUser('/login')

    messages = Message.query.filter(
        Message.user_id == session['user-id']).all()
    user = User.query.get_or_404(user_id)

    return render_template('/users/show.html', messages=messages, user=session['user-id'])


@app.route('/users/edit', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    checkForUser('/')

    user = session['user-id']
    form = EditProfileForm()

    if form.validate_on_submit():
        if form.username.data:
            user.username = form.username.data

        if form.password.data:
            user.password = bcrypt.generate_password_hash( form.password.data ).decode('UTF-8')

        db.session.commit()
        return redirect("/ticker")

    return render_template('/users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    checkForUser('/')

    Message.query.filter(Message.user_id == session['user-id']).delete()

    if session.get('user-id') is not None:
        del session['user-id']

    db.session.delete(session['user-id'])
    db.session.commit()

    flash("Account Deleted", "success")

    return redirect("/signup")

##############################################################################
# Messages routes:


@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """
    checkForUser('/')

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data, ticker=form.ticker.data.upper(), title=form.title.data)
        user = User.query.get(session['user-id'])
        user.posts.append(msg)
        db.session.commit()

        return redirect("/")

    return render_template('messages/new.html', form=form)


@app.route('/messages/show')
def pull_messages():
    """ Display Individual Messages"""

    messages = Message.query.all()

    return render_template('/messages/display.html', messages=messages)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    checkForUser('/')

    msg = Message.query.get_or_404(message_id)
    if msg.user_id != session['user-id']:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{session['user-id']}")


##############################################################################
# Homepage and error pages

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('/users/404.html')


# ##############################################################################
# Turn off all caching in Flask

# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers['Cache-Control'] = 'public, max-age=0'
#     return req
