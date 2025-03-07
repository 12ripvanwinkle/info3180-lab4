import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, Flask, send_from_directory, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm
from app import db
from app.models import UserProfile
from werkzeug.security import check_password_hash
from .forms import UploadForm, LoginForm

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg'}

# Create the app instance
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm()


    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        file = form.image.data

        
        # Secure the filename to prevent directory traversal attacks
        filename = secure_filename(file.filename)

        # Check if the file is allowed
        if not allowed_file(filename):
            flash('Invalid file type. Only image files (jpg, png, jpeg, gif) are allowed.', 'danger')
            return redirect(url_for('upload'))
        
        # Save the file to the upload folder
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        flash('File Saved', 'success')
        return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template("upload.html", form=form)

def get_uploaded_images():
    upload_folder = os.path.join(app.root_path, 'uploads')
    uploaded_files = []

    # Check if the folder exists before attempting to access it
    if not os.path.exists(upload_folder):
        print(f"Upload folder '{upload_folder}' does not exist.")
        return uploaded_files  # Return an empty list if folder doesn't exist

    # Walk through the directory and get filenames
    for subdir, dirs, files in os.walk(upload_folder):
        for file in files:
            # Append only image files (optional: filter extensions)
            if file.lower().endswith(('.png', '.jpg')):
                uploaded_files.append(file)
    
    print(f"Found {len(uploaded_files)} images: {uploaded_files}")
    return uploaded_files
    
@app.route('/uploads/<filename>')
@login_required
def get_image(filename):
    """Serve an uploaded image by filename."""
    upload_folder = os.path.join(current_app.root_path, 'uploads')  # Ensure 'uploads' folder is correct
    return send_from_directory(upload_folder, filename)

@app.route('/files')
@login_required
def files():
    """List all uploaded files."""
    images = get_uploaded_images()  # Get the list of uploaded images
    print(f"Images to display: {images}")  # Debugging line
    return render_template('files.html', images=images)

@app.route('/logout')
@login_required
def logout():
    """Logs out the user and flashes a message."""
    logout_user()  # Logs out the user
    flash('You have been logged out successfully!', 'success')  # Flash a success message
    return redirect(url_for('home'))  # Redirect to the home route

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data

        # Using your model, query database for a user based on the username
        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):  # Check if user exists and passwords match
            # User is authenticated, log them in
            login_user(user)
            flash('You have successfully logged in!', 'success')  # Flash success message
            return redirect(url_for('upload.html'))  # Redirect to the home page
        else:
            # If username or password is incorrect, flash an error message
            flash('Invalid username or password', 'danger')
        
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        # Gets user id, load into session
        # answer
        login_user(user)

        # Remember to flash a message to the user
        return redirect(url_for('upload'))  # The user should be redirected to the upload form instead
    return render_template("login.html", form=form)

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     return render_template('upload.html')  # Render the upload page template

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
