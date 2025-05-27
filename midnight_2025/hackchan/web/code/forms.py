from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=7, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=9, max=80)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=7, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=9, max=80)])
    submit = SubmitField('Login')
