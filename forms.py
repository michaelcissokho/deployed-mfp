from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length, Optional


class TickerLookup(FlaskForm):
    """form to lookup ticker"""

    ticker = StringField('Enter Ticker Here', validators=[DataRequired()])

class SignupForm(FlaskForm):
    """ form to signup a user """

    username = StringField('Create Username')
    password = PasswordField('Create Password')

class LoginForm(FlaskForm):
    """ form to login a user """

    username = StringField('Enter Your Username')
    password = PasswordField('Enter Your Password')

class MessageForm(FlaskForm):
    """ form to create a post """

    ticker = StringField("Enter Ticker You're Writing About")
    title = StringField("Title of Your Post")
    text = TextAreaField('Write Your Post Here')
    
class EditProfileForm(FlaskForm):
    """ form to edit a user's profile """

    username = StringField("Enter New Username", [Optional()])
    password = PasswordField("Enter New Password", [Optional()])
