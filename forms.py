from flask_wtf import Form
from wtforms import (StringField, PasswordField, DateField,
                     IntegerField, TextAreaField)
from wtforms.validators import DataRequired, Email, Length, EqualTo


class SignUpForm(Form):
    """The form for registration"""
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(validators=[DataRequired(), EqualTo('password')])


class SignInForm(Form):
    """Form for signing in"""
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])


class JournalCreateForm(Form):
    """Form for creating and editing journals.
    Tags are not included in editing"""
    title = StringField(u'Title', validators=[DataRequired()])
    date = DateField(u'Date', format='%m/%d/%Y', validators=[DataRequired()])
    time_spent = IntegerField(u'Time Spent', validators=[DataRequired()])
    learned_info = TextAreaField(u'What I Learned',
                                 validators=[DataRequired()])
    resources = TextAreaField(u'Resources to Remember',
                              validators=[DataRequired()])
    tags = StringField(u'Tag(s)')
