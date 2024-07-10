# Import necessary modules
import extrafunc
import csvfunc
from extfun import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session
import flask
import envfile
import userenum
import platform_type
from datetime import datetime
host = envfile.host                                    # Get host from envfile
username = envfile.dbuser                              # Get username from envfile
password = envfile.dbpass                              # Get password from envfile
dbname = envfile.dbname                                # Get dbname from envfile
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import requests
# set the environment variable for the google api testing
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'



# Initialize Flask application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "Data"
ALLOWED_EXTENSIONS = {'csv'}

# Set a secret key for session management
app.secret_key = 'your secret key'

# Initialize VidSchool object with database connection parameters
vidschool = VidSchool(host, username, password, dbname)

# Route for '/' and '/login', handles both GET and POST requests

@app.route('/view_videos/csv', methods=['GET', 'POST'])
def csvhandler():
    return csvfunc.rendercsv(request, vidschool)

@app.route('/view_videos/csv/addcsv', methods=['POST'])
def addcsv():
    author = {                                                     # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                         # Get user id from session
        "user_email": session.get("user_email"),                   # Get user email from session
        "user_type": session.get("user_type"),                     # Get user type from session
    }
    return csvfunc.csv2sql(request, vidschool, author)


# Set a secret key for session management
app.secret_key = 'your secret key'

# Initialize VidSchool object with database connection parameters
vidschool = VidSchool(host, username, password, dbname)

# Route for '/' and '/login', handles both GET and POST requests
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])                      
def login():
    msg = ''                                            # Initialize message to empty string
    
    # Check if POST request with 'user_email' and 'password' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form:        # Check if POST request with 'user_email' and 'password' in form data
        user_email = request.form['user_email']                                                         # Get user email from form data
        password = request.form['password']                                                             # Get password from form data

        # Call external function to validate user credentials
        valid = vidschool.login_user(user_email, password)

        # If credentials are valid
        if valid and valid.get('success'):                        # Check if valid is not None and 'success' key is True
            session['loggedin'] = True                            # Set 'loggedin' session variable to True
            session['username'] = user_email                      # Set 'username' session variable to user email
            session['user_type'] = valid['user_type']             # Set 'user_type' session variable to user type
            session['user_id'] = valid['user_id']                 # Set 'user_id' session variable to user id
            msg = 'Logged in successfully !'                      # Set message
            return render_template('index.html', msg=msg)         # Redirect to home page
        else:                                                     # If credentials are invalid
            msg = "Login Failed!! Contact Administrator"          # Set message if credentials are invalid
            return render_template('login.html', msg=msg)         # Render login.html template with current message
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)                 

# Route for '/index'
@app.route('/index')
def index():
    if 'loggedin' in session:                            # Check if user is logged in
        return render_template('index.html')             # Render index.html template if user is logged in
    else:                                                # If user is not logged in
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
        user_name = request.form['user_name']                          # Get user name from form data
        user_email = request.form['user_email']                        # Get user email from form data
        password = request.form['password']                            # Get password from form data
        user_type = request.form['user_type']                          # Get user type from form data
        author = {                                                     # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                         # Get user id from session
            "user_email": session.get("user_email"),                   # Get user email from session
            "user_type": session.get("user_type"),                     # Get user type from session
        }

        # Call external function to add user
        try:
            vidschool.add_user(user_name,user_email, password, user_type, author)     # Add user with user_email, password and user_type
            msg = 'User added successfully!'                                          # Set message

        except Exception as e:                                           # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                     # Show error message
    return render_template('add_user.html', msg=msg)                     # Render add_user.html template with current message

# Route for '/viewusers' to view all users
@app.route('/view_users')
def view_users():
    if 'loggedin' not in session or session.get('user_type') != 0:       # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                # Redirect to login page if user is not logged in or is not an admin
    
    author = {                                                         # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                             # Get user id from session
        "user_email": session.get("user_email"),                       # Get user email from session
        "user_type": session.get("user_type"),                         # Get user type from session
    }

    users = vidschool.get_users(author)                                # Get all users from external function
    roles = userenum.roletype                                          # Get all user roles from userenum module
    status=userenum.userstatus                                         # Get all user status from userenum module

    # Render view_users.html template with users data
    return render_template('view_users.html', users=users,roles=roles,status=status)             

# Route for '/edituser' to edit a user with user_id
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'loggedin' not in session or session.get('user_type') != 0:      # Check if user is logged in and is an admin
        return redirect(url_for('login'))                               # Redirect to login page if user is not logged in or is not an admin
    
    author = {                                                          # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                              # Get user id from session
        "user_email": session.get("user_email"),                        # Get user email from session
        "user_type": session.get("user_type"),                          # Get user type from session
    }

    if request.method == 'POST':                                        # Check if POST request with 'user_email', 'password' and 'user_type' in form data
        user_name = request.form['user_name']                           # Get user name from form data
        user_email = request.form['user_email']                         # Get user email from form data
   
        user_type = request.form['user_type']                           # Get user type from form data
        status = request.form['status']                                 # Get user status from form data
        try:
            vidschool.edit_user(user_name,user_id, user_email, user_type,status, author)        # Edit user with user_id, user_email, password and user_type
            return redirect(url_for('view_users'))                                              # Redirect to view_users page after editing user
        except Exception as e:                                                                  # Catch any exceptions and show error message
            return f'Error: {str(e)}'                                                           # Show error message
    
    user = vidschool.get_user(user_id)                                                 # Get user with user_id
    status=userenum.userstatus                                                         # Get all user status from userenum module
    return render_template('edit_user.html', user=user,status=status)                               # Render edit_user.html template with user

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
        msg = 'User deleted successfully!'                                           # Set success message
    except Exception as e:                                                           # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                     # Show error message
    
    return redirect(url_for('view_users',msg=msg))                                   # Redirect to view_users page after deleting user

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
    
    msg = ''                                                                            # Initialize message to empty string
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        url = request.form['url']                                                        # Get URL from form data
        
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.add_video(video_title=video_title,url=url,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,author=author)                                                  
            msg = 'Video added successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    
    channels = vidschool.get_channels()                                                                             # Get all channels
    # Render add_video.html template with current message and users data for each role 
    return render_template('add_video.html', msg=msg,channels=channels)                                             # Render add_video.html template with current message

# Route for '/viewchannnel' to view all videos
@app.route('/add_channel', methods=['GET', 'POST'])
def add_channel():
    if 'loggedin' not in session or session.get('user_type') != 0:    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                             # Redirect to login page if user is not logged in or is not an admin
    msg = ''
    
    # Check if POST request with 'channel_name', 'url' and 'platform' in form data
    if request.method == 'POST' and 'channel' in request.form and 'platform' in request.form: 
        channel_name = request.form['channel']                   # Get channel name from form data                             # Get URL from form data
        platform = request.form['platform']                           # Get platform from form data
        creator_id = request.form['creator_id']                       # Get creator from form data
        editor_id = request.form['editor_id']                         # Get editor from form data
        manager_id = request.form['manager_id']                       # Get manager from form data
        ops_id = request.form['ops_id']                               # Get ops from form data
        author = {                                                    # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                        # Get user id from session
            "user_email": session.get("user_email"),                  # Get user email from session
            "user_type": session.get("user_type"),                    # Get user type from session
        }

        try:
            vidschool.add_channel(channel_name, platform, creator_id, editor_id, manager_id, ops_id, author)  # Add channel with channel_name, URL,platform, creator_id, editor_id, manager_id, ops_id
            msg = 'Channel added successfully!'                                                                    # Set success message

        except Exception as e:                                          # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                    # Show error message

    # Fetch users for each role
    creators = vidschool.get_users_by_role(4)                                                                     # Get all creators
    editors = vidschool.get_users_by_role(3)                                                                      # Get all editors
    managers = vidschool.get_users_by_role(1)                                                                     # Get all managers
    opss = vidschool.get_users_by_role(2)                                                                         # Get all opss
    channels = vidschool.get_channels()                                                                           # Get all channels

    # Render add_channel.html template with current message and users data for each role
    return render_template('add_channel.html', msg=msg, creators=creators, editors=editors, managers=managers, opss=opss, channels=channels)            

# Route for '/viewchannnel' to view all videos
@app.route('/view_channels')
def view_channels():
    if 'loggedin' not in session or session.get('user_type') !=0:              # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin

    try:
        channels = vidschool.get_channels()                                     # Get all channels
        platform_id = platform_type.platform_names                              # Get all platform types from platform_type module
        creators = vidschool.get_users_by_role(4)                               # Get all creators
        creator_dict = {creator[0]: creator[1] for creator in creators}         # Create dictionary with creator id as key and creator name as value
        editors = vidschool.get_users_by_role(3)                                # Get all editors
        editor_dict = {editor[0]: editor[1] for editor in editors}              # Create dictionary with editor id as key and editor name as value
        managers = vidschool.get_users_by_role(1)                               # Get all managers
        manager_dict = {manager[0]: manager[1] for manager in managers}         # Create dictionary with manager id as key and manager name as value
        opss = vidschool.get_users_by_role(2)                                   # Get all opss
        ops_dict = {ops[0]: ops[1] for ops in opss}                             # Create dictionary with ops id as key and ops name as value
    except Exception as e:                                                      # Catch any exceptions and show error message
        channels = []                                                           # Set channels to empty list
        msg = f'Error: {str(e)}'                                                # Show error message

        # Render view_channels.html template with channels data and error message
        return render_template('view_channels.html', channels=channels, msg=msg)         
    
    # Render view_channels.html template with channels data and users data for each role
    return render_template('view_channels.html', channels=channels,platform_id=platform_id,creator_dict=creator_dict,editor_dict=editor_dict,manager_dict=manager_dict,ops_dict=ops_dict, msg='')  # Render view_channels.html template with channels data

# Route for '/editchannel' to edit a channel with channel_id
@app.route('/edit_channel/<int:channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    if 'loggedin' not in session or session.get('user_type') != 0:             # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    msg = ''                                                                   # Initialize message to empty string

    # Fetch the channel details to pre-fill the form
    channel = vidschool.get_channel(channel_id)

    if request.method == 'POST':                                                 # Check if POST request with 'channel_name', 'url, 'platform', 'creator_id', 'editor_id', 'manager_id', 'ops_id' and 'status' in form data
        channel_name = request.form.get('channel_name')                          # Get channel name from form data    
        url = request.form.get('url')                                            # Get URL from form data 
        platform = request.form.get('platform')                                  # Get platform from form data
        creator_id = request.form['creator_id']                                  # Get creator from form data
        editor_id = request.form['editor_id']                                    # Get editor from form data
        manager_id = request.form['manager_id']                                  # Get manager from form data
        ops_id = request.form['ops_id']                                          # Get ops from form data
        status = request.form.get('status')                                      # Get status from form data
        author = {                                                               # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                   # Get user id from session 
            "user_email": session.get("user_email"),                             # Get user email from session
            "user_type": session.get("user_type"),                               # Get user type from session
        }

         # Try to edit channel with channel_id, channel_name, URL,platform, creator_id, editor_id, manager_id, ops_id, status
        try:   
            # Call external function to edit channel with channel_id, channel_name, URL,platform, creator_id, editor_id, manager_id, ops_id, status                                                                       
            vidschool.edit_channel(channel_id, channel_name, platform, creator_id, editor_id, manager_id, ops_id,status, author)

            msg = 'Channel updated successfully!'                                      # Set success message
            return redirect(url_for('view_channels'))                                  # Redirect to view_channels page after editing channel
        except Exception as e:                                                         # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                   # Show error message

    # Fetch users for each role
    creators = vidschool.get_users_by_role(4)                                                                     # Get all creators
    editors = vidschool.get_users_by_role(3)                                                                      # Get all editors
    managers = vidschool.get_users_by_role(1)                                                                     # Get all managers
    opss = vidschool.get_users_by_role(2)                                                                         # Get all opss
    channels = vidschool.get_channels()                                                                           # Get all channels

    # Render edit_channel.html template with current message, channel data and users data for each role
    return render_template('edit_channel.html', channel=channel, msg=msg , creators=creators, editors=editors, managers=managers, opss=opss, channels=channels)             

# Route for '/deletechannel' to delete a channel with channel_id
@app.route('/delete_channel/<int:channel_id>')
def delete_channel(channel_id):
    if 'loggedin' not in session or session.get('user_type') != 0:                       # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                                # Redirect to login page if user is not logged in or is not an admin

    author = {                                                                           # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                               # Get user id from session
        "user_email": session.get("user_email"),                                         # Get user email from session
        "user_type": session.get("user_type"),                                           # Get user type from session
    }

    try:                                                                                 # Try to delete channel with channel_id
        vidschool.delete_channel(channel_id, author)                                     # Delete channel with channel_id
        msg = 'Channel deleted successfully!'                                            # Set success message
    except Exception as e:                                                               # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                         # Show error message

    return redirect(url_for('view_channels', msg=msg))                                   # Redirect to view_channels page after deleting channel

# Route for '/updatechannelstatus' to update channel status
@app.route('/update_channel_status/<int:channel_id>', methods=['POST'])
def update_channel_status(channel_id):
    if 'loggedin' not in session or session.get('user_type') != 0:                       # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                                # Redirect to login page if user is not logged in or is not an admin

    new_status = request.form.get('status')                                              # Get new status from form data
    author = {                                                                           # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                               # Get user id from session
        "user_email": session.get("user_email"),                                         # Get user email from session
        "user_type": session.get("user_type"),                                           # Get user type from session
    }

    try:                                                                                 # Try to update channel status with channel_id and new_status
        vidschool.update_channel_status(channel_id, new_status, author)                  # Update channel status with channel_id and new_status
        msg = 'Channel status updated successfully!'                                     # Set success message
    except Exception as e:                                                               # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                         # Show error message

    return redirect(url_for('view_channels', msg=msg))                                   # Redirect to view_channels page after updating channel status
 
# Route for '/view_videos' to view all videos
@app.route('/view_videos')
def view_videos():
  
    author = {                                                                           # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                               # Get user id from session
        "user_email": session.get("user_email"),                                         # Get user email from session
        "user_type": session.get("user_type"),                                           # Get user type from session
    }
    
    try:                                                                                # Try to get all videos
        channels = vidschool.get_channels()                                             # Get all channels
        channel_dict = {channel[0]: channel[1] for channel in channels}                 # Create dictionary with channel id as key and channel name as value
        videos = vidschool.get_videos(author)                                           # Get all videos
        
        # Render view_videos.html template with videos data and users data for each role
        return render_template('view_videos.html', videos=videos,channels=channels,channel_dict=channel_dict)                       # Render view_videos.html template with videos
    
    except Exception as e:                                                              # Catch any exceptions and show error message
        return render_template('index.html', error=str(e))                              # Render index.html template with error message

# Route for '/editvideo' to edit a video with video_id
# Route for editing a video
@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    if 'loggedin' not in session:                                                       # Check if user is logged in
        return redirect(url_for('login'))                                               # Redirect to login page if user is not logged in

    msg = ''                                                                            # Initialize message to empty string

    video = vidschool.get_video(video_id)                                               # Get video with video_id
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        status = request.form['status']                                                 # Get video status from form data
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        comment=request.form['comment']
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.update_video(video_id=video_id,video_title=video_title,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,status=status,comment=comment,author=author)                                                  
            msg = 'Video updated successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    # Fetch users for each role
    
    channels = vidschool.get_channels()                                                                           # Get all channels
    author= {
        "user_type": session.get("user_type")
    }
    # Render edit_video.html template with video and users data for each role
    return render_template('edit_video.html', video=video,channels=channels, msg=msg,author=author)                                                # Render edit_video.html template with video and message

# Route for '/deletevideo' to delete a video with video_id
# Route for deleting a video
@app.route('/delete_video/<int:video_id>', methods=['GET'])
def delete_video(video_id):
    if 'loggedin' not in session:                                                       # Check if user is logged in
        return redirect(url_for('login'))                                               # Redirect to login page if user is not logged in

    author = {                                                                          # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                              # Get user id from session
        "user_email": session.get("user_email"),                                        # Get user email from session
        "user_type": session.get("user_type"),                                          # Get user type from session
    }

    try:                                                                                # Try to delete video with video_id
        vidschool.set_delete_video(video_id, author)                                    # Delete video with video_id
        msg = 'Video deleted successfully!'                                             # Set success message
    except Exception as e:                                                              # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                        # Show error message

    return redirect(url_for('view_videos', msg=msg))                                    # Redirect to view_videos page after deleting video

# Route for '/updatevideostatus' to update video status
# Route for updating video status
@app.route('/update_video_status', methods=['POST'])
def update_video_status():
    if 'loggedin' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in

    video_id = request.form['video_id']
    status = request.form['status']  # Get new status from form data
    comment = request.form['comment']
    author = {  # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),  # Get user id from session
        "user_email": session.get("user_email"),  # Get user email from session
        "user_type": session.get("user_type"),  # Get user type from session
    }

    try:  # Try to update video status with video_id and status
        vidschool.set_video_status(int(video_id), int(status), author, comment)  # Update video status with video_id and status
        msg = 'Video status updated successfully!'  # Set success message
    except Exception as e:  # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'  # Show error message

    return redirect(url_for('view_videos', msg=msg))  # Redirect back to view_videos page after updating


@app.route('/view_channels_manager')
def view_channels_manager():
    if 'loggedin' not in session or session.get('user_type') != 1:             # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin

    try:
        user_id = session['user_id']                                           # Get the logged-in user's ID
        user_type = session['user_type']                                       # Get the logged-in user's type
  
        # Fetch channels managed by the logged-in user
        channels = vidschool.get_channels_by_user(user_id, user_type)         
        platform_id = platform_type.platform_names                              # Get all platform types from platform_type modulele
        creators = vidschool.get_users_by_role(4)                               # Get all creators
        creator_dict = {creator[0]: creator[1] for creator in creators}         # Create dictionary with creator id as key and creator name as value
        editors = vidschool.get_users_by_role(3)                                # Get all editors
        editor_dict = {editor[0]: editor[1] for editor in editors}              # Create dictionary with editor id as key and editor name as value
        managers = vidschool.get_users_by_role(1)                               # Get all managers
        manager_dict = {manager[0]: manager[1] for manager in managers}         # Create dictionary with manager id as key and manager name as value
        opss = vidschool.get_users_by_role(2)                                   # Get all opss
        ops_dict = {ops[0]: ops[1] for ops in opss}                             # Create dictionary with ops id as key and ops name as value
    except Exception as e:                                                      # Catch any exceptions and show error message
        channels = []                                                           # Set channels to empty list
        msg = f'Error: {str(e)}'                                                # Show error message

        # Render view_channels.html template with channels data and error message
        return render_template('view_channels.html', channels=channels, msg=msg)

    # Render view_channels.html template with channels data
    return render_template('view_channels.html', channels=channels,platform_id=platform_id,creator_dict=creator_dict,editor_dict=editor_dict,manager_dict=manager_dict,ops_dict=ops_dict, msg='')

# Route for '/addvideo_manager', handles both GET and POST requests
@app.route('/add_video_manager', methods=['GET', 'POST'])
def add_video_manager():
    if 'loggedin' not in session or session.get('user_type') not in [0, 1]:            # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                              # Redirect to login page if user is not logged in or is not an admin or manager
    
    msg = ''                                                                            # Initialize message to empty string
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        status = request.form['status']                                                 # Get video status from form data
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.add_video(video_title=video_title,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,status=status,author=author)                                                  
            msg = 'Video added successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    user_id = session['user_id']                                           # Get the logged-in user's ID
    user_type = session['user_type']                                       # Get the logged-in user's type
    channels = vidschool.get_channels_by_user(user_id,user_type)                                                                             # Get all channels
    # Render add_video.html template with current message and users data for each role 
    return render_template('add_video_manager.html', msg=msg,channels=channels)                                             # Render add_video.html template with current message

@app.route('/view_videos_manager')
def view_videos_manager():
    if 'loggedin' not in session or session.get('user_type') != 1:             # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    
    try:                                                                               
            author = {                                                                           # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                               # Get user id from session
            "user_email": session.get("user_email"),                                         # Get user email from session
            "user_type": session.get("user_type"),                                           # Get user type from session
            }
            
            channels = vidschool.get_channels()                                              # Get all channels
            channel_dict = {channel[0]: channel[1] for channel in channels}                 # Create dictionary with channel id as key and channel name as value
            videos = vidschool.get_videos(author)                                           # Get all videos
            
            # Render view_videos.html template with videos data and users data for each role
            return render_template('view_videos_manager.html', videos=videos,channels=channels,channel_dict=channel_dict)                       # Render view_videos.html template with videos
            
            
    except Exception as e:                                                              # Catch any exceptions and show error message
        return render_template('index.html', error=str(e))                              # Render index.html template with error message

@app.route('/view_users_manager')
def view_users_manager():
    msg = ''                                                                            # Initialize message to empty string
    if 'loggedin' not in session or session.get('user_type') != 1:                    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                             # Redirect to login page if user is not logged in or is not an admin
    try:                                                                                # Try to get all users
        user_id = session['user_id']                                           # Get the logged-in user's ID
        user_type = session['user_type']                                       # Get the logged-in user's type
        channels=vidschool.get_channels_by_user(user_id=user_id,user_type=user_type)                                            # Get all channels
        creators = vidschool.get_users_by_role(4)                               # Get all creators
        creator_dict = {creator[0]: creator[1] for creator in creators}         # Create dictionary with creator id as key and creator name as value
        editors = vidschool.get_users_by_role(3)                                # Get all editors
        editor_dict = {editor[0]: editor[1] for editor in editors}              # Create dictionary with editor id as key and editor name as value
        opss = vidschool.get_users_by_role(2)                                   # Get all opss
        ops_dict = {ops[0]: ops[1] for ops in opss}
           # Render view_users.html template with users
    except Exception as e:                                                              # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                        # Show error message
        return render_template('index.html', msg=msg)                                   # Render index.html template with error message
    
    return render_template('view_users_manager.html', channels=channels,creator_dict=creator_dict,editor_dict=editor_dict,ops_dict=ops_dict,msg=msg)

@app.route('/view_videos_editor')
def view_videos_editor():
    if 'loggedin' not in session or session.get('user_type') != 3:             # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    msg = ''
    try:                                                                               
        
        author = {                                                                           # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                               # Get user id from session
            "user_email": session.get("user_email"),                                         # Get user email from session
            "user_type": session.get("user_type"),                                           # Get user type from session
            }
        # Fetch videos managed by the logged-in user
        videos = vidschool.get_videos(author=author)                      
        channels=vidschool.get_channels()                                            # Get all channels
        channel_dict = {channel[0]: channel[1] for channel in channels}              # Create dictionary with channel id as key and channel name as value
        
    
    except Exception as e:                                                              # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                        # Show error message
        return render_template('index.html', msg=msg)                              # Render index.html template with error message

    return render_template('view_videos_editor.html', videos=videos,channel_dict=channel_dict,msg=msg)                       # Render view_videos.html template with videos

@app.route('/view_channels_editor')
def view_channels_editor():
    if 'loggedin' not in session or session.get('user_type') != 3:             # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin

    try:
        user_id = session['user_id']                                           # Get the logged-in user's ID
        user_type = session['user_type']                                       # Get the logged-in user's type
  
        # Fetch channels managed by the logged-in user
        channels = vidschool.get_channels_by_user(user_id, user_type)         
        platform_id = platform_type.platform_names                              # Get all platform types from platform_type modulele
        creators = vidschool.get_users_by_role(4)                               # Get all creators
        creator_dict = {creator[0]: creator[1] for creator in creators}         # Create dictionary with creator id as key and creator name as value
        editors = vidschool.get_users_by_role(3)                                # Get all editors
        editor_dict = {editor[0]: editor[1] for editor in editors}              # Create dictionary with editor id as key and editor name as value
        managers = vidschool.get_users_by_role(1)                               # Get all managers
        manager_dict = {manager[0]: manager[1] for manager in managers}         # Create dictionary with manager id as key and manager name as value
        opss = vidschool.get_users_by_role(2)                                   # Get all opss
        ops_dict = {ops[0]: ops[1] for ops in opss}                             # Create dictionary with ops id as key and ops name as value
    except Exception as e:                                                      # Catch any exceptions and show error message
        channels = []                                                           # Set channels to empty list
        msg = f'Error: {str(e)}'                                                # Show error message

        # Render view_channels.html template with channels data and error message
        return render_template('view_channels_editor.html', channels=channels, msg=msg)

    # Render view_channels.html template with channels data
    return render_template('view_channels_editor.html', channels=channels,platform_id=platform_id,creator_dict=creator_dict,editor_dict=editor_dict,manager_dict=manager_dict,ops_dict=ops_dict, msg='')

@app.route('/add_video_creator', methods=['GET', 'POST'])
def add_video_creator():
    if 'loggedin' not in session or session.get('user_type') != 4:            # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    msg = ''                                                                    # Initialize message to empty string
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        status = request.form['status']                                                 # Get video status from form data
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.add_video(video_title=video_title,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,status=status,author=author)                                                  
            msg = 'Video added successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    user_id = session['user_id']                                           # Get the logged-in user's ID
    user_type = session['user_type']                                       # Get the logged-in user's type
    channels = vidschool.get_channels_by_user(user_id,user_type)                                                                             # Get all channels
    # Render add_video.html template with current message and users data for each role 
    return render_template('add_video_creator.html', msg=msg,channels=channels)

@app.route('/view_videos_creator')
def view_videos_creator():
    if 'loggedin' not in session or session.get('user_type') != 4:             # Check if user is logged in and is an admin or manager
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    msg = ''
    try:                                                                                       
        author = {                                                                           # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                               # Get user id from session
            "user_email": session.get("user_email"),                                         # Get user email from session
            "user_type": session.get("user_type"),                                           # Get user type from session
            }
        user_id = session['user_id']                                           # Get the logged-in user's ID
        user_type = session['user_type']                                       # Get the logged-in user's type
        # Fetch videos managed by the logged-in user
        videos = vidschool.get_videos(author=author)                      
        channels=vidschool.get_channels_by_user(user_id,user_type)                                            # Get all channels
        channel_dict = {channel[0]: channel[1] for channel in channels}              # Create dictionary with channel id as key and channel name as value
        
    
    except Exception as e:                                                              # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                        # Show error message
        return render_template('index.html', msg=msg)                              # Render index.html template with error message

    return render_template('view_videos_creator.html', videos=videos,channel_dict=channel_dict,msg=msg)                       # Render view_videos.html template with videos

@app.route('/edit_video_creator/<int:video_id>', methods=['GET', 'POST'])
def edit_video_creator(video_id):
    if 'loggedin' not in session:                                                       # Check if user is logged in
        return redirect(url_for('login'))                                               # Redirect to login page if user is not logged in

    msg = ''                                                                            # Initialize message to empty string

    video = vidschool.get_video(video_id)                                               # Get video with video_id
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        status = request.form['status']                                                 # Get video status from form data
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        comment=request.form['comment']
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.update_video(video_id=video_id,video_title=video_title,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,status=status,comment=comment,author=author)                                                  
            msg = 'Video updated successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message

    channels = vidschool.get_channels()                                                                           # Get all channels
 
    # Render edit_video.html template with video and users data for each role
    return render_template('edit_video_creator.html', video=video,channels=channels, msg=msg)                                                # Render edit_video.html template with video and message

@app.route('/add_video_ops', methods=['GET', 'POST'])
def add_video_ops():
    if 'loggedin' not in session or session.get('user_type') != 2 :            
        return redirect(url_for('login'))                                              # Redirect to login page if user is not logged in or is not an admin or manager
    
    msg = ''                                                                            # Initialize message to empty string
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id' and 'manager_id' in form data
        video_title = request.form['video_name']                                         # Get video name from form data
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        status = request.form['status']                                                 # Get video status from form data
         # Convert datetime strings to Unix timestamps if provided, otherwise set to None
        shoot_timestamp = request.form['shoot_timestamp']
        shoot_timestamp = int(datetime.strptime(shoot_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if shoot_timestamp else None
        
        edit_timestamp = request.form['edit_timestamp']
        edit_timestamp = int(datetime.strptime(edit_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if edit_timestamp else None
        
        upload_timestamp = request.form['upload_timestamp']
        upload_timestamp = int(datetime.strptime(upload_timestamp, '%Y-%m-%dT%H:%M').timestamp()) if upload_timestamp else None
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id,oops_id
            vidschool.add_video(video_title=video_title,channel_id=channel_id,shoot_timestamp=shoot_timestamp,edit_timestamp=edit_timestamp,upload_timestamp=upload_timestamp,status=status,author=author)                                                  
            msg = 'Video added successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    user_id = session['user_id']                                           # Get the logged-in user's ID
    user_type = session['user_type']                                       # Get the logged-in user's type
    channels = vidschool.get_channels_by_user(user_id,user_type)                                                                             # Get all channels
    # Render add_video.html template with current message and users data for each role 
    return render_template('add_video_ops.html', msg=msg,channels=channels)



# Custom Jinja2 filter for datetime formatting
@app.template_filter('datetimeformat')
def datetimeformat(value):
    if value is None:
        return ''
    return datetime.fromtimestamp(value).strftime('%Y-%m-%dT%H:%M')

# Register the filter
app.jinja_env.filters['datetimeformat'] = datetimeformat

@app.route('/view_channel_details/<int:channel_id>')
def view_channel_details(channel_id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    msg = ''
    try:
        channel = vidschool.get_channel(channel_id)
        return render_template('view_channel_details.html', channel=channel)
    except Exception as e:
        msg = f'Error: {str(e)}'
        return render_template('index.html', msg=msg)

#youtube api implementation
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly',
          'https://www.googleapis.com/auth/yt-analytics.readonly',
          'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
          'https://www.googleapis.com/auth/userinfo.profile'
          ]  
API_SERVICE_NAME1 = 'youtubeAnalytics'
API_VERSION1 = 'v2'
METRICS = [
    "views",
    "redViews",
    "comments",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
    "subscribersGained",
    "subscribersLost"
]

# Oauth page 1
@app.route('/oauth')
def oauth():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    auth_url,state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    flask.session['state'] = state
    
    return flask.redirect(auth_url)

# Oauth page 2
@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    auth_response = flask.request.url
    flow.fetch_token(authorization_response=auth_response)
    
    credentials = flow.credentials
    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.channels().list(
        part="snippet",
        mine=True
    )
    response = request.execute()
    if response['items']:
        channel_name = response['items'][0]['snippet']['title']
    else:
        channel_name = "No channel found"
    flask.session['channel_name'] = channel_name  # Store channel name in session
    flask.session['credentials'] = credentials.to_json()
    print(flask.session['credentials'])
    return flask.redirect(flask.url_for("add_channel"))




# Main entry point of the application
if __name__ == '__main__':
    vidschool.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True, port=8080,host='localhost')                                            # Run the Flask application in debug mode
