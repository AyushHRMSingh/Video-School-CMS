# Import necessary modules
from extfun import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session
import envfile

host = envfile.host
username = envfile.dbuser
password = envfile.dbpass
dbname = envfile.dbname

# Initialize Flask application
app = Flask(__name__)


# Set a secret key for session management
app.secret_key = 'your secret key'

# Initialize VidSchool object with database connection parameters
vidschool = VidSchool(host, username, password, dbname)

# Route for '/' and '/login', handles both GET and POST requests
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])  
def login():
    msg = ''
    
    # Check if POST request with 'user_email' and 'password' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form:
        user_email = request.form['user_email']                   # Get user email from form data
        password = request.form['password']                       # Get password from form data

        # Call external function to validate user credentials
        valid = vidschool.login_user(user_email, password)

        # If credentials are valid
        if valid and valid.get('success'):
            session['loggedin'] = True                            # Set 'loggedin' session variable to True
            session['username'] = user_email
            session['user_type'] = valid['user_type']             # Set 'username' session variable to user email
            msg = 'Logged in successfully !'                      # Set message
            return render_template('index.html', msg=msg)         # Redirect to home page
        else:
            msg = "Login Failed!! Contact Administrator"          # Set message if credentials are invalid
            return render_template('login.html', msg=msg)
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)                 

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html')             # Render index.html template if user is logged in
    else:
        return redirect(url_for('login'))                # Redirect to login page if user is not logged in
    
# Route for '/logout'
@app.route('/logout')
def logout():
    # Clear session variables related to login
    session.pop('loggedin', None)                                # Clear 'loggedin' session variable
    session.pop('id', None)                                      # Clear 'id' session variable
    session.pop('username', None)                                # Clear 'user_email' session variable
    session.pop('user_type', None)                               # Clear 'user_type' session variable
    return redirect(url_for('login'))                            # Redirect to login page after logout

# Route for '/adduser', handles both GET and POST requests
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'loggedin' not in session or session.get('user_type') != 0:    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                             # Redirect to login page if user is not logged in or is not an admin
    msg = ''

    # Check if POST request with 'user_email', 'password' and 'user_type' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form and 'user_type' in request.form:
        user_email = request.form['user_email']                       # Get user email from form data
        password = request.form['password']                           # Get password from form data
        user_type = request.form['user_type']                         # Get user type from form data
        author = {
            "user_id": session.get("user_id"),                         # Get user id from session
            "user_email": session.get("user_email"),                   # Get user email from session
            "user_type": session.get("user_type"),                     # Get user type from session
        }

        # Call external function to add user
        try:
            vidschool.add_user(user_email, password, user_type, author)     # Add user with user_email, password and user_type
            msg = 'User added successfully!'

        except Exception as e:                                           # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                     # Show error message
    return render_template('add_user.html', msg=msg)                     # Render add_user.html template with current message

# Route for '/viewusers' to view all users
@app.route('/view_users')
def view_users():
    if 'loggedin' not in session or session.get('user_type') != 0:       # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                # Redirect to login page if user is not logged in or is not an admin
    
    author = {
        "user_id": session.get("user_id"),                             # Get user id from session
        "user_email": session.get("user_email"),                       # Get user email from session
        "user_type": session.get("user_type"),                         # Get user type from session
    }

    users = vidschool.get_users(author)                                # Get all users from external function
    return render_template('view_users.html', users=users)             # Render view_users.html template with users

# Route for '/edituser' to edit a user with user_id
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'loggedin' not in session or session.get('user_type') != 0:      # Check if user is logged in and is an admin
        return redirect(url_for('login'))                               # Redirect to login page if user is not logged in or is not an admin
    
    author = {
        "user_id": session.get("user_id"),                              # Get user id from session
        "user_email": session.get("user_email"),                        # Get user email from session
        "user_type": session.get("user_type"),                          # Get user type from session
    }

    if request.method == 'POST':                                        # Check if POST request with 'user_email', 'password' and 'user_type' in form data
        user_email = request.form['user_email']                         # Get user email from form data
        password = request.form['password']                             # Get password from form data
        user_type = request.form['user_type']                           # Get user type from form data

        try:
            vidschool.edit_user(user_id, user_email, password, user_type, author)     # Edit user with user_id, user_email, password and user_type
            return redirect(url_for('view_users'))                                    # Redirect to view_users page after editing user
        except Exception as e:                                                        # Catch any exceptions and show error message
            return f'Error: {str(e)}'                                                 # Show error message
    
    user = vidschool.get_user(user_id)                                                # Get user with user_id
    return render_template('edit_user.html', user=user)                               # Render edit_user.html template with user

# Route for '/deleteuser' to delete a user with user_id
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'loggedin' not in session or session.get('user_type') != 0:                   # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                            # Redirect to login page if user is not logged in or is not an admin
    
    author = {                                                                       # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                           # Get user id from session
        "user_email": session.get("user_email"),                                     # Get user email from session
        "user_type": session.get("user_type"),                                       # Get user type from session
    }

    try:                                                                             # Try to delete user with user_id
        vidschool.delete_user(user_id, author)                                       # Delete user with user_id
        msg = 'User deleted successfully!'
    except Exception as e:                                                           # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'
    
    return redirect(url_for('view_users'))                                           # Redirect to view_users page after deleting user

# Route for '/viewvideos' to view all videos
@app.route('/view_logs')
def view_logs():
    if 'loggedin' not in session or session.get('user_type') != 0:                    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                             # Redirect to login page if user is not logged in or is not an admin
    
    logs = vidschool.get_logs()                                                       # Get all logs from external function
    
    return render_template('view_logs.html', logs=logs)                               # Render view_logs.html template with logs

# Route for '/addvideo', handles both GET and POST requests
@app.route('/add_video', methods=['GET', 'POST'])
def add_video():
    if 'loggedin' not in session or session.get('user_type') not in [0, 1]:            # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                              # Redirect to login page if user is not logged in or is not an admin or manager
    
    msg = ''
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_name = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']
        creator_id = request.form['creator_id']                                         # Get creator id from form data
        editor_id = request.form['editor_id']                                           # Get editor id from form data
        manager_id = request.form['manager_id']                                         # Get manager id from form data
        operator_id = request.form['operator_id']                                       # Get operator id from form data
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                        # Try to add video with video_name, creator_id, editor_id, manager_id
            vidschool.add_video(video_name, channel_id, creator_id, editor_id, manager_id, operator_id, author)   # Add video with video_name, creator_id, editor_id, manager_id
            msg = 'Video added successfully!'                                                       # Set message
        except Exception as e:                                                                      # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'
    
    return render_template('add_video.html', msg=msg)                                                # Render add_video.html template with current message

# Main entry point of the application
if __name__ == '__main__':
    vidschool.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True)                                            # Run the Flask application in debug mode
