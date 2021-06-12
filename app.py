from flask import Flask, render_template, jsonify, request, session, g,redirect, flash
from sqlalchemy import exc
from flask_bcrypt import Bcrypt
from forms import TickerLookup,SignupForm,LoginForm,MessageForm,EditProfileForm
from models import db, connect_db, User, Message
from constants import secret_key, api_key_secret, database
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database
CURR_USER_KEY = "curr_user"

bcrypt = Bcrypt()
connect_db(app)
db.create_all()

api_key = api_key_secret
link = 'https://financialmodelingprep.com/api/v3'


def send_return_data(data_from_api):
    # creating dict to retrieve all information from api and convert into internal dictionary
    return_data = dict()

    # send jsonify'd data back to "[somethhing-statement]Data" function in script.js
    for key,value in data_from_api.items():
        return_data[key] = value

    return jsonify(return_data)

##########################################################
#ticker data routes

@app.route('/ticker')
def get_ticker_data():
    # used to call index.html file

    return render_template('/users/ticker.html')

@app.route('/profile-data', methods = ['POST'])
def get_profile_data():
    ticker = request.json.get('ticker').upper()

    # route will call financialmodelingprep.com API, I preset the params in advance because of errors connecting backend to front
    res = requests.get(f'{link}/profile/{ticker}?apikey={api_key}')

    data = res.json()[0]

    return send_return_data(data)

@app.route('/income-statement-data', methods = ['POST'])
def get_income_statement():
    limit = request.json.get('limit')
    ticker = request.json.get('ticker').upper()

    res = requests.get(f'{link}/income-statement/{ticker}?limit={limit}&apikey={api_key}')

    # res.json()[0] necessary based on structure of response we get from API
    data = res.json()[0]

    return send_return_data(data)


@app.route('/balance-sheet-statement-data', methods = ['POST'])
def get_balance_sheet():
    limit = request.json.get('limit')
    ticker = request.json.get('ticker').upper()

    res = requests.get(f'{link}/balance-sheet-statement/{ticker}?limit={limit}&apikey={api_key}')

    data = res.json()[0]

    return send_return_data(data)


@app.route('/cash-flow-statement-data', methods = ['POST'])
def get_cash_flow_statement():

    limit = request.json.get('limit')
    ticker = request.json.get('ticker').upper()

    res = requests.get(f'{link}/cash-flow-statement/{ticker}?limit={limit}&apikey={api_key}')

    data = res.json()[0]

    return send_return_data(data)

@app.route('/historical-price-data', methods = ['POST'])
def get_historical_data():
    ticker = request.json.get('ticker').upper()

    res = requests.get(f'{link}/historical-price-full/{ticker}?apikey={api_key}')

    data = res.json()

    return send_return_data(data)


##########################################
# homepage data routes
@app.route('/home')
def homepage():

    return render_template('/users/home.html')

@app.route('/market-index-data', methods = ['POST'])
def get_market_index_data():

    res = requests.get(f'{link}/quotes/index/?apikey={api_key}')

    # comes back as a list of dictionaries
    data = res.json()

    # this attribute was removed and made available by only premium members of the API

    return jsonify(data)

@app.route('/market-news', methods = ['POST'])
def get_market_news():

    res = requests.get(f'{link}/stock_news?apikey={api_key}')

    data = res.json()

    return jsonify(data)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
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

        do_login(user)

        return redirect("/home")

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
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/home")

        flash("Invalid credentials.", 'danger')

    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/users/login")



##############################################################################
# General user routes:

@app.route('/users/<int:user_id>')
def show_profile(user_id):
    if not g.user:
        flash('Access unauthorized', 'danger')
        return redirect('/login')

    messages = Message.query.filter(Message.user_id == g.user.id).all()
    user = User.query.get_or_404(user_id)

    return render_template('/users/show.html', messages = messages, user = g.user)


@app.route('/users/edit', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/home")

    user = g.user
    form = EditProfileForm()

    if form.validate_on_submit():
        if form.username.data:
            user.username = form.username.data

        if form.password.data:
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            user.password = hashed_pwd

        db.session.commit()
        return redirect("/ticker")

    return render_template('/users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/home")

    Message.query.filter(Message.user_id == g.user.id).delete()

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    flash ("Account Deleted", "success")

    return redirect("/signup")

##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/home")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data, ticker = form.ticker.data.upper(), title = form.title.data)
        g.user.posts.append(msg)
        db.session.commit()

        return redirect("/home")

    return render_template('messages/new.html', form=form, user = g.user)

@app.route('/messages/show')
def pull_messages():
    """ Display Individual Messages"""

    messages = Message.query.all()

    return render_template('/messages/display.html', messages = messages)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/home")

    msg = Message.query.get_or_404(message_id)
    if msg.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/home")

    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('/users/404.html')


# ##############################################################################
# # Turn off all caching in Flask

# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers['Cache-Control'] = 'public, max-age=0'
#     return req
