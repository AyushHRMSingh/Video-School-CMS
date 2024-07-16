# Import necessary modules
import ast
import json
import extra_functions as extra_functions
import csv_functions
from type_vars import *
import type_vars
import stat_functions
from external_function import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import user_enumeration, video_enumeration, channel_enumeration, general_log_enumeration
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import yaml
import os
import math

# Find Root Path
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables from env.yml file
with open(os.path.join(PROJECT_PATH+'/env.yml')) as file:
    env = yaml.load(file, Loader=yaml.FullLoader)

# Extract database connection parameters from environment variables
host = env['dbvar']['host']
username = env['dbvar']['dbuser']
password = env['dbvar']['dbpass']
dbname = env['dbvar']['dbname']

# set the environment variable for the google api testing
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#youtube api implementation
CLIENT_SECRETS_FILE = "Source/client_secrets.json"
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['UPLOAD_FOLDER'] = "Data"
ALLOWED_EXTENSIONS = {'csv'}
app.secret_key = 'your secret key'


# Redirect request for favicon to static folder
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# root path
@app.route('/')
def base():
    # print(session)
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if POST request with 'user_email' and 'password' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form:       
        user_email = request.form['user_email']                                                        
        password = request.form['password']                                                            
        # Call external function to validate user credentials
        valid = cmsobj_db.login_user(user_email, password)
        # If credentials are valid
        if valid and valid.get('success'):               
            session['loggedin'] = True                   
            session['username'] = user_email             
            session['user_type'] = valid['user_type']    
            session['user_id'] = valid['user_id']        
            msg = 'Logged in successfully !'             
            return redirect(url_for('dashboard'))
        else:                                            
            msg = "Login Failed!! Contact Administrator" 
            return render_template('login.html', msg=msg)
    # Render login.html template with current message (empty message)    
    return render_template('login.html', msg=msg)

# User logout, deletes all session variables
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('user_type', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            # return "Admin Dashboard"
            return render_template('dashboard.html', sessionvar=session, user=user_enumeration.roletype)
        elif session['user_type'] in [USER_TYPE_MANAGER, USER_TYPE_CREATOR, USER_TYPE_EDITOR, USER_TYPE_OPS]:
            channellist = cmsobj_db.get_channels_by_user(session['user_id'], session['user_type'])
            # return "Manager Dashboard"
            return render_template('dashboard.html', sessionvar=session, channels=channellist, user=user_enumeration.roletype)
    else:
        return redirect(url_for('login'))


@app.route('/users')
def view_users():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            users = cmsobj_db.get_users(author=author)
            roles = user_enumeration.roletype
            status = user_enumeration.userstatus
            return render_template('view_user.html', users=users, roles=roles, status=status)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # print(request.form.to_dict())
                result = cmsobj_db.edit_user(request.form.to_dict(), author)
                if result!=True:
                    return result
                return redirect(url_for('view_users'))
            user = cmsobj_db.get_user(user_id)
            return render_template('edit_user.html', user=user)
        else:
            return "You are not authorized to view sthis page"
    else:
        return redirect(url_for('login'))

@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = cmsobj_db.delete_user(user_id, author)
            if result!=True:
                return result
            elif result == True:
                return redirect(url_for('view_users'))
        else:
            return "You are not authorized to view this page"

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                result = cmsobj_db.add_user(request.form.to_dict(), author)
                if result!=True:
                    return render_template('add_user.html', msg=result)
                else:
                    return render_template('add_user.html', msg="User added Successfully")
            return render_template('add_user.html')
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/channels')
def view_all_channels():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            channels = cmsobj_db.get_channels()
            users = cmsobj_db.get_users(author=author)
            finaluserlist = {}
            for user in list(users):
                if user[5] == USER_STATUS_INACTIVE:
                    finaluserlist[user[0]] = "INACTIVE USER"
                else:
                    finaluserlist[user[0]] = user[1]
            return render_template('view_all_channels.html', channels=channels, user=finaluserlist, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))


@app.route('/view/<int:channel_id>/stat')
def view_channel_stats(channel_id):
    if session.get('loggedin'):
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        stats = None
        if channel[0] in VidSchool.credentialpool:
            stats = stat_functions.get_main(channel[1], channel[0])
        return render_template('view_channel_stats.html', sessionvar=session, channel=channel, stats=stats)
    else:
        return redirect(url_for('login'))


@app.route('/channels/edit/<int:channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # print(request.form.to_dict())
                # return request.form.to_dict()
                result = cmsobj_db.edit_channel(request.form.to_dict(), author)
                if result!=True:
                    return result
                if 'addcredentials' in session:
                    # print("linking channel")
                    linkres = link_channel(channel_id)
                    if linkres!=True:
                        return linkres
                return redirect(url_for('view_all_channels'))
            channel = cmsobj_db.get_channel(channel_id)
            creator = cmsobj_db.get_users_by_role(4)
            editor = cmsobj_db.get_users_by_role(3)
            ops = cmsobj_db.get_users_by_role(2)
            manager = cmsobj_db.get_users_by_role(1)
            return render_template('edit_channel.html', channel=channel, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/channels/add', methods=['GET', 'POST'])
def add_channel():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            channel_name = None
            if "temp_channel_name" in session:
                channel_name = session["temp_channel_name"]
            creator = cmsobj_db.get_users_by_role(4)
            editor = cmsobj_db.get_users_by_role(3)
            ops = cmsobj_db.get_users_by_role(2)
            manager = cmsobj_db.get_users_by_role(1)
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                if "temp_channel_name" in session:
                    session.pop("temp_channel_name")
                channel_id = cmsobj_db.add_channel(request.form.to_dict(), author)
                if type(channel_id)!=int:
                    return channel_id
                elif type(channel_id)==int:
                    if "addcredentials" in session:
                        result = link_channel(channel_id)
                        if result!=True:
                            return result
                        else:
                            return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg="Channel added and linked Successfully")
                    else:
                        return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg="Channel added Successfully")
            return render_template('add_channel.html', channel_name=channel_name, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/channels/link/<int:channel_id>', methods=['GET','POST'])
def link_channel(channel_id):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                tokens = json.dumps(session['addcredentials'])
                session.pop('addcredentials')
                # print(tokens)
                result = cmsobj_db.link_channel(channel_id=channel_id, token=tokens, author=author)
                if result!=True:
                    return result
                else:
                    return True
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/channels/unlink/<int:channel_id>')
def unlink_channel(channel_id):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = cmsobj_db.unlink_channel(channel_id, author)
            if result!=True:
                return result
            elif result == True:
                return redirect(request.referrer)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/view/<int:channel_id>')
def view_single_channel(channel_id):
    if session.get('loggedin'):
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        # get all videos associated with a channel
        videos = cmsobj_db.get_videos_by_channel(channel_id)
        # reverse the list the list to show the latest videos
        videos.reverse()
        # make another list to store videos in as the databse output is immutable
        final_video_list = []
        # add the videos to the final list and convert the epoch time to string
        for i in videos:
            final_video_list.append([i[0], i[1], i[2], i[3], i[4], extra_functions.epoch_to_string(i[5],'date'), extra_functions.epoch_to_string(i[6],'date'), extra_functions.epoch_to_string(i[7],'date'), i[8], i[9]])
        # make a dictionary to store the user details of the channel
        users = {}
        # get the user details of the channel and store into dict
        for i in range(3,7):
            user = cmsobj_db.get_user(channel[i])
            if user[5] == USER_STATUS_INACTIVE:
                users[channel[i]] = [user[1], "INACTIVE USER"]
            else:
                users[channel[i]] = [user[1], user[2]]
        return render_template('view_channel.html', sessionvar=session,channel=channel, videos=final_video_list, users=users, platform=channel_enumeration.platform_names, status=video_enumeration.vidstatus)
    else:
        return redirect(url_for('login'))

@app.route('/view/<int:channel_id>/add_video', methods=['GET', 'POST'])
def add_video(channel_id):
    if session.get('loggedin'):
        if session["user_type"] not in [USER_TYPE_ADMIN, USER_TYPE_MANAGER, USER_TYPE_OPS, USER_TYPE_CREATOR]:
            return "You are not authorized to add videos"
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = cmsobj_db.add_video(request.form.to_dict(), author)
            if result!=True:
                return result
            else:
                return render_template('add_video.html', sessionvar=session, channel=channel, msg="Video added Successfully")
        return render_template('add_video.html', sessionvar=session, channel=channel)
    else:
        return redirect(url_for('login'))

@app.route('/update', methods=['GET', 'POST'])
def update_status():
    if session.get('loggedin'):
        author = {
            'user_id': session['user_id'],
            'user_type': session['user_type']
        }
        result = cmsobj_db.set_video_status(request.form.to_dict(), author)
        if result!=True:
            return result
        # return "you updated"
        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))

@app.route('/edit/video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    if session.get('loggedin'):
        video = cmsobj_db.get_video(video_id)
        channel_id = video[4]
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            passreq = request.form.to_dict()
            passreq['shoot_timestamp'] = extra_functions.string_to_epoch(passreq['shoot_timestamp'])
            passreq['edit_timestamp'] = extra_functions.string_to_epoch(passreq['edit_timestamp'])
            passreq['upload_timestamp'] = extra_functions.string_to_epoch(passreq['upload_timestamp'])
            # print(passreq)
            # result = True
            result = cmsobj_db.edit_video(passreq, author)
            if result!=True:
                return result
            return redirect(url_for('view_single_channel', channel_id=request.form['channel_id']))
        video = cmsobj_db.get_video(video_id)
        finalvidlist = list(video)
        for i in range(5,8):
            finalvidlist[i] = extra_functions.epoch_to_string(finalvidlist[i], 'date')
            print(finalvidlist[i])
        return render_template('edit_video.html', channel=channel, sessionvar=session, video=finalvidlist)
    else:
        return redirect(url_for('login'))

@app.route('/logs/p=<int:pagenum>')
def get_logs(pagenum):
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            output = cmsobj_db.get_logs_by_page(pagenum-1)
            logs = output[0]
            number_of_pages = math.ceil(output[1]/100)
            finallogs = []
            finaluserlist = {}
            users = cmsobj_db.get_users(author=author)
            for log in logs:
                finallogs.append([log[0], log[1], extra_functions.epoch_to_string(log[2], 'datetime'), ast.literal_eval(log[3].replace('null', 'None'))])
            for user in list(users):
                finaluserlist[user[0]] = [user[1], user[2]]
            return render_template('view_logs.html', logs=finallogs, users=finaluserlist, action=general_log_enumeration.log_type, pagenum=pagenum, number_of_pages=number_of_pages)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# Oauth page 1
@app.route('/oauth')
def oauth():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    auth_url,state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    session['state'] = state
    session['return_url'] = request.referrer
    return redirect(auth_url)

# Oauth page 2
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    auth_response = request.url
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
    
    # store channels name and credentials in session
    session['temp_channel_name'] = channel_name
    session['addcredentials'] = extra_functions.credtodict(credentials)
    # print(session['addcredentials'])
    return_url = session['return_url']
    session.pop('return_url')
    return redirect(return_url)

# Main entry point of the application
if __name__ == '__main__':
    # cmsobj_db.setupdb()
    cmsobj_db = VidSchool(host, username, password, dbname)
    app.run(debug=True, port=8089,host='localhost')
