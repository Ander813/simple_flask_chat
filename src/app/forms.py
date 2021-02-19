from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(), Email()])
    password = StringField(
        label="password", validators=[DataRequired(), Length(min=8, max=50)]
    )


class RegisterForm(FlaskForm):
    email = StringField(label="email", validators=[DataRequired(), Email()])
    password1 = StringField(
        label="password1", validators=[DataRequired(), Length(min=8, max=50)]
    )
    password2 = StringField(
        label="password2",
        validators=[DataRequired(), Length(min=8, max=50), EqualTo("password1")],
    )
