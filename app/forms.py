from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, DataRequired
from wtforms import FileField, SubmitField
from flask_wtf.file import FileRequired, FileAllowed


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class UploadForm(FlaskForm):
    # upload an image file thing
    image = FileField('Upload Image', validators=[DataRequired(message="Please upload an image"), FileAllowed(['jpg','png'], message="Only JPG and PNG files are allowed.")])
    pass