# Import necessary modules
from extfun import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.middleware.proxy_fix import ProxyFix
import envfile

host = envfile.host
username = envfile.dbuser
password = envfile.dbpass
dbname = envfile.dbname

# Initialize Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

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
        if valid['success']:
            session['loggedin'] = True                            # Set 'loggedin' session variable to True
            session['username'] = user_email
            session['user_type'] = valid['user_type']             # Set 'username' session variable to user email
            msg = 'Logged in successfully !'                      # Set message
            return render_template('index.html', msg=msg)         # Redirect to home page
        else:
            msg = "Incorrect username / password !"               # Set message if credentials are invalid
        
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)                 

@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))
    
# Route for '/logout'
@app.route('/logout')
def logout():
    # Clear session variables related to login
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)                              # Clear 'user_email' session variable
    session.pop('user_type', None)
    return redirect(url_for('login'))                            # Redirect to login page after logout

# Route for '/register', handles GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''                                                    # Initialize message variable
    
    # Check if POST request with 'user_email' and 'password' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form:
        user_email = request.form['user_email']                # Get user email from form data
        password = request.form['password']                    # Get password from form data

        # Call external function to add user (assuming it validates and adds to database)
        valid = vidschool.add_user(user_email, password,'USER_ADMIN')  # Add user with role 'user'

        msg = "User added"                                     # Set message

    # Render register.html template with current message 
    return render_template('register.html', msg=msg)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'loggedin' not in session or session.get('user_type') != 'USER_ADMIN':
        return redirect(url_for('login'))
    msg = ''
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form and 'user_type' in request.form:
        user_email = request.form['user_email']
        password = request.form['password']
        user_type = request.form['user_type']
        try:
            vidschool.add_user(user_email, password, user_type)
            msg = 'User added successfully!'
        except Exception as e:
            msg = f'Error: {str(e)}'
    return render_template('add_user.html', msg=msg)

# Main entry point of the application
if __name__ == '__main__':
    vidschool.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True)                                       # Run the Flask application in debug mode
