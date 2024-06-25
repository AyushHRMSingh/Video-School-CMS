# Import necessary modules
import extfun
from flask import Flask, render_template, request, redirect, url_for, session

# Initialize Flask application
app = Flask(__name__)

# Set a secret key for session management
app.secret_key = 'your secret key'

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
        valid = extfun.login_user(user_email, password)

        # If credentials are valid
        if valid['success']:
            session['loggedin'] = True                            # Set 'loggedin' session variable to True
            session['username'] = user_email                      # Set 'username' session variable to user email
            msg = 'Logged in successfully !'                      # Set message
            return render_template('index.html', msg=msg)         # Redirect to home page
        else:
            msg = "Incorrect username / password !"               # Set message if credentials are invalid
        
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)                 

# Route for '/logout'
@app.route('/logout')
def logout():
    # Clear session variables related to login
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)                              # Clear 'user_email' session variable
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
        valid = extfun.add_user(user_email, password,'USER_ADMIN')  # Add user with role 'user'

        msg = "User added"                                     # Set message

    # Render register.html template with current message 
    return render_template('register.html', msg=msg)

# Main entry point of the application
if __name__ == '__main__':
    extfun.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True)                                       # Run the Flask application in debug mode
