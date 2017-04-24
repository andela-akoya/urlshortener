# coding=utf-8
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class AuthenticationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z0-9_.]*$',
                                              message='Username must have '
                                                      'only letters,numbers, '
                                                      'dots or underscores')])


class RegistrationForm(AuthenticationForm):
    lastname = StringField('Lastname', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z]*$',
                                              message='Lastname must have '
                                                      'only letters ')])
    firstname = StringField('Firstname', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z]*$',
                                              message='Firstname must have '
                                                      'only letters ')])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField("Password", validators=[
        DataRequired(), EqualTo('confirm_password',
                                message="Passwords don't match")])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(AuthenticationForm):
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Login')


