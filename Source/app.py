# Import necessary modules
from extfun import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session
import envfile
import userenum
import platform_type

host = envfile.host                                    # Get host from envfile
username = envfile.dbuser                              # Get username from envfile
password = envfile.dbpass                              # Get password from envfile
dbname = envfile.dbname                                # Get dbname from envfile

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
            session['username'] = user_email                      # Set 'username' session variable to user email
            session['user_type'] = valid['user_type']             # Set 'user_type' session variable to user type
            msg = 'Logged in successfully !'                      # Set message
            return render_template('index.html', msg=msg)         # Redirect to home page
        else:
            msg = "Login Failed!! Contact Administrator"          # Set message if credentials are invalid
            return render_template('login.html', msg=msg)
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)                 

@app.route('/index')
def index():
    if 'loggedin' in session:                            # Check if user is logged in
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
            msg = 'User added successfully!'                                # Set message

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
    roles = userenum.roletype                                           # Get all user roles from userenum module
    status=userenum.userstatus
    return render_template('view_users.html', users=users,roles=roles,status=status)             # Render view_users.html template with users

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
        user_name = request.form['user_name']                          # Get user name from form data
        user_email = request.form['user_email']                         # Get user email from form data
        password = request.form['password']                             # Get password from form data
        user_type = request.form['user_type']                           # Get user type from form data

        try:
            vidschool.edit_user(user_name,user_id, user_email, password, user_type, author)     # Edit user with user_id, user_email, password and user_type
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
        msg = f'Error: {str(e)}'                                                     # Show error message
    
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
        channel_id = request.form['channel_id']                                         # Get channel id from form data
        creator_id = request.form['creator_id']                                         # Get creator id from form data
        editor_id = request.form['editor_id']                                           # Get editor id from form data
        manager_id = request.form['manager_id']                                         # Get manager id from form data
        ops_id = request.form['ops_id']                                       # Get ops id from form data
        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                      # Try to add video with video_name, creator_id, editor_id, manager_id
            vidschool.add_video(channel_id, video_name, creator_id, editor_id, manager_id, ops_id, author)   # Add video with video_name, creator_id, editor_id, manager_id
            msg = 'Video added successfully!'                                                                     # Set message
        except Exception as e:                                                                                    # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                              # Show error message
    
    # Fetch users for each role
    creators = vidschool.get_users_by_role(4)                                                                     # Get all creators
    editors = vidschool.get_users_by_role(3)                                                                      # Get all editors
    managers = vidschool.get_users_by_role(1)                                                                     # Get all managers
    opss = vidschool.get_users_by_role(2)                                                                         # Get all opss
    channels = vidschool.get_channels()                                                                           # Get all channels

    return render_template('add_video.html', msg=msg, creators=creators, editors=editors, managers=managers, opss=opss, channels=channels)       # Render add_video.html template with current message

# Route for '/viewchannnel' to view all videos
@app.route('/add_channel', methods=['GET', 'POST'])
def add_channel():
    if 'loggedin' not in session or session.get('user_type') != 0:    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                             # Redirect to login page if user is not logged in or is not an admin
    msg = ''

    if request.method == 'POST' and 'channel_name' in request.form and 'url' in request.form and 'platform' in request.form:
        channel_name = request.form['channel_name']                   # Get channel name from form data
        url = request.form['url']                                     # Get URL from form data
        platform = request.form['platform']                           # Get platform from form data
        creator_id = request.form['creator_id']                             # Get creator from form data
        editor_id = request.form['editor_id']                               # Get editor from form data
        manager_id = request.form['manager_id']                             # Get manager from form data
        ops_id = request.form['ops_id']                                     # Get ops from form data
        author = {                                                    # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                        # Get user id from session
            "user_email": session.get("user_email"),                  # Get user email from session
            "user_type": session.get("user_type"),                    # Get user type from session
        }

        try:
            vidschool.add_channel(channel_name, url, platform, creator_id, editor_id, manager_id, ops_id, author)  
            msg = 'Channel added successfully!'                        # Set success message

        except Exception as e:                                          # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                    # Show error message

    # Fetch users for each role
    creators = vidschool.get_users_by_role(4)                                                                     # Get all creators
    editors = vidschool.get_users_by_role(3)                                                                      # Get all editors
    managers = vidschool.get_users_by_role(1)                                                                     # Get all managers
    opss = vidschool.get_users_by_role(2)                                                                         # Get all opss
    channels = vidschool.get_channels()                                                                           # Get all channels

    return render_template('add_channel.html', msg=msg, creators=creators, editors=editors, managers=managers, opss=opss, channels=channels)            

# Route for '/viewchannnel' to view all videos
@app.route('/view_channels')
def view_channels():
    if 'loggedin' not in session or session.get('user_type') != 0:    # Check if user is logged in and is an admin
        return redirect(url_for('login'))                             # Redirect to login page if user is not logged in or is not an admin

    try:
        channels = vidschool.get_channels()                            # Get all channels
        platform_id = platform_type.platform_names                      # Get all platform types from platform_type module
        creators = vidschool.get_users_by_role(4)                    # Get all creators
        creator_dict = {creator[0]: creator[1] for creator in creators}
        editors = vidschool.get_users_by_role(3)                     # Get all editors
        editor_dict = {editor[0]: editor[1] for editor in editors}
        managers = vidschool.get_users_by_role(1)                    # Get all managers
        manager_dict = {manager[0]: manager[1] for manager in managers}
        opss = vidschool.get_users_by_role(2)                        # Get all opss
        ops_dict = {ops[0]: ops[1] for ops in opss}
    except Exception as e:                                             # Catch any exceptions and show error message
        channels = []                                                  # Set channels to empty list
        msg = f'Error: {str(e)}'                                       # Show error message
        return render_template('view_channels.html', channels=channels, msg=msg)          # Render view_channels.html template with channels data and error message
    
    return render_template('view_channels.html', channels=channels,platform_id=platform_id,creator_dict=creator_dict,editor_dict=editor_dict,manager_dict=manager_dict,ops_dict=ops_dict, msg='')  # Render view_channels.html template with channels data

# Route for '/editchannel' to edit a channel with channel_id
@app.route('/edit_channel/<int:channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    if 'loggedin' not in session or session.get('user_type') != 0:             # Check if user is logged in and is an admin
        return redirect(url_for('login'))                                      # Redirect to login page if user is not logged in or is not an admin
    msg = ''                                                                   # Initialize message to empty string

    # Fetch the channel details to pre-fill the form
    channel = vidschool.get_channel(channel_id)

    if request.method == 'POST':                                               # Check if POST request with 'channel_name', 'url' and 'platform' in form data
        channel_name = request.form.get('channel_name')                        # Get channel name from form data    
        url = request.form.get('url')                                          # Get URL from form data 
        platform = request.form.get('platform')                                # Get platform from form data
        creator_id = request.form['creator_id']                             # Get creator from form data
        editor_id = request.form['editor_id']                               # Get editor from form data
        manager_id = request.form['manager_id']                             # Get manager from form data
        ops_id = request.form['ops_id']                                     # Get ops from form data
        author = {                                                             # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                 # Get user id from session 
            "user_email": session.get("user_email"),                           # Get user email from session
            "user_type": session.get("user_type"),                             # Get user type from session
        }

        try:                                                                           # Try to edit channel with channel_id, channel_name, URL, and platform
            vidschool.edit_channel(channel_id, channel_name, url, platform, creator_id, editor_id, manager_id, ops_id, author)   
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
        videos = vidschool.get_videos(author)                                           # Get all videos
        return render_template('view_videos.html', videos=videos)                       # Render view_videos.html template with videos
    
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
    if request.method == 'POST':                                                        # Check if POST request with 'video_name', 'creator_id', 'editor_id', 'manager_id' and 'ops_id' in form data
        video_name = request.form.get('video_name')                                     # Get video name from form data
        creator_id = request.form.get('creator_id')                                     # Get creator id from form data
        editor_id = request.form.get('editor_id')                                       # Get editor id from form data
        manager_id = request.form.get('manager_id')                                     # Get manager id from form data
        ops_id = request.form.get('ops_id')                                   # Get ops id from form data
        

        author = {                                                                      # Author dictionary with user_id, user_email and user_type
            "user_id": session.get("user_id"),                                          # Get user id from session
            "user_email": session.get("user_email"),                                    # Get user email from session
            "user_type": session.get("user_type"),                                      # Get user type from session
        }

        try:                                                                                                       # Try to update video with video_id, video_name, creator_id, editor_id, manager_id, ops_id
            vidschool.update_video(video_id, video_name, creator_id, editor_id, manager_id, ops_id, author)   # Update video with video_id, video_name, creator_id, editor_id, manager_id,ops_id
            msg = 'Video updated successfully!'                                                                    # Set success message
        except Exception as e:                                                                                     # Catch any exceptions and show error message
            msg = f'Error: {str(e)}'                                                                               # Show error message

    return render_template('edit_video.html', video=video, msg=msg)                                                # Render edit_video.html template with video and message

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
@app.route('/update_video_status/<int:video_id>', methods=['POST'])
def update_video_status(video_id):
    if 'loggedin' not in session:                                                       # Check if user is logged in
        return redirect(url_for('login'))                                               # Redirect to login page if user is not logged in

    status = request.form['status']                                                     # Get new status from form data
    author = {                                                                          # Author dictionary with user_id, user_email and user_type
        "user_id": session.get("user_id"),                                              # Get user id from session
        "user_email": session.get("user_email"),                                        # Get user email from session
        "user_type": session.get("user_type"),                                          # Get user type from session
    }

    try:                                                                                # Try to update video status with video_id and status
        vidschool.set_video_status(video_id, int(status), author)                       # Update video status with video_id and status
        msg = 'Video status updated successfully!'                                      # Set success message
    except Exception as e:                                                              # Catch any exceptions and show error message
        msg = f'Error: {str(e)}'                                                        # Show error message

    return redirect(url_for('view_videos', msg=msg))                                    # Redirect back to view_videos page after updating


# Main entry point of the application
if __name__ == '__main__':
    vidschool.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True)                                            # Run the Flask application in debug mode
