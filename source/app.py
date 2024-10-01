# Import necessary modules
import ast
import json
import extra_functions as extra_functions
from csv_functions import *
from type_vars import *
from werkzeug.utils import secure_filename
import stat_functions
import stat_functions_edited
from external_function import VidSchool
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import flask
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

# create database object
cmsobj_db = VidSchool(host, username, password, dbname)

# set the environment variable for the google api testing
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#youtube api implementation
CLIENT_SECRETS_FILE = os.path.join(PROJECT_PATH, 'client_secrets.json')
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['UPLOAD_FOLDER'] = os.path.join(PROJECT_PATH, 'Data')
ALLOWED_EXTENSIONS = {'csv'}
app.secret_key = 'your secret key'

@app.context_processor
def inject_user():
    if 'loggedin' not in session:
        return dict(user=None)
    author = {
        'user_id': session['user_id'],
        'user_type': session['user_type']
    }
    channels_list = cmsobj_db.get_channels()
    users_list = cmsobj_db.get_users(author=author)
    return dict(clist=channels_list, ulist=users_list)

# Redirect request for favicon to static folder
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

# root path
@app.route('/')
def base():
    # checks for session variables
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

# Home page for all users
@app.route('/dashboard')
def dashboard():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            # return "Admin Dashboard"
            return render_template('dashboard.html', sessionvar=session, user=user_enumeration.roletype)
        elif session['user_type'] in [USER_TYPE_MANAGER, USER_TYPE_CREATOR, USER_TYPE_EDITOR, USER_TYPE_OPS]:
            channellist = cmsobj_db.get_channels_by_user(session['user_id'], session['user_type'])
            # return "Manager Dashboard"
            return render_template('dashboard.html', sessionvar=session, channels=channellist, user=user_enumeration.roletype, test="testingval")
    else:
        return redirect(url_for('login'))

# page to view list of all users in the system
@app.route('/users')
def view_users():
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # get list of all users
            users = cmsobj_db.get_users(author=author)
            # get dictionary of all roles
            roles = user_enumeration.roletype
            # get dictionary of all user status types
            status = user_enumeration.userstatus
            return render_template('view_user.html', users=users, roles=roles, status=status)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to edit user details for specified user
@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # checks for login session
    if session.get('loggedin'):
        # checks if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            user = cmsobj_db.get_user(user_id)
            # checks if request is POST then considered api request
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # call external function to edit user details
                result = cmsobj_db.edit_user(request.form.to_dict(), author)
                # if result is not True then return the result
                if result!=True:
                    return render_template('edit_user.html', user=user, msg=result)
                # if result is True then redirect to view users page
                return redirect(url_for('view_users'))
            return render_template('edit_user.html', user=user)
        else:
            return "You are not authorized to view sthis page"
    else:
        return redirect(url_for('login'))

# page to delete user
@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # call external function to delete user
            result = cmsobj_db.delete_user(user_id, author)
            # if result is not True then return the result
            if result!=True:
                return result
            # if result is True then redirect to view users page
            elif result == True:
                return redirect(url_for('view_users'))
        else:
            return "You are not authorized to view this page"

# page to add users in the system
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            # check if request is POST then considered api request
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # call external function to add user
                result = cmsobj_db.add_user(request.form.to_dict(), author)
                # if result is not True then return the result
                if result!=True:
                    return render_template('add_user.html', msg=result)
                # if result is True return successful message to the user
                else:
                    return render_template('add_user.html', msg="User added Successfully")
            # render add_user.html template
            return render_template('add_user.html')
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to view all channels in the system
@app.route('/channels')
def view_all_channels():
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # get list of all channels
            channels = cmsobj_db.get_channels()
            # get list of all users
            users = cmsobj_db.get_users(author=author)
            # make a dictionary to store the user details of the channel
            final_user_list = {}
            for user in list(users):
                # if user is inactive then show INACTIVE USER
                if user[5] == USER_STATUS_INACTIVE:
                    final_user_list[user[0]] = "INACTIVE USER"
                else:
                    final_user_list[user[0]] = user[1]
            return render_template('view_all_channels.html', channels=channels, user=final_user_list, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to view the statistics of the specifed channel
@app.route('/view/<int:channel_id>/stat')
def view_channel_stats(channel_id):
    # check for login session
    if session.get('loggedin'):
        # get the channel details
        channel = cmsobj_db.get_channel(channel_id)
        # check if the user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        # create variable to store channel stats
        stats = None
        linked = False
        # check if the channel has credentials
        if channel[0] in VidSchool.credentialpool:
            # stats = stat_functions.get_main(channel[0])
            linked = True
        # return the view_channel_stats.html template
        return render_template('view_channel_stats.html', sessionvar=session, channel=channel, linked=linked)
    else:
        return redirect(url_for('login'))

## ORIGINAL function
# page to view the statistics of the specifed channel
# @app.route('/view/<int:channel_id>/stat')
# def view_channel_stats(channel_id):
#     # check for login session
#     if session.get('loggedin'):
#         # get the channel details
#         channel = cmsobj_db.get_channel(channel_id)
#         # check if the user is linked to the channel
#         if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
#             return "You are not authorized to view this page"
#         # create variable to store channel stats
#         stats = None
#         # check if the channel has credentials
#         if channel[0] in VidSchool.credentialpool:
#             stats = stat_functions.get_main(channel[0])
#         # return the view_channel_stats.html template
#         return render_template('view_channel_stats_notedited.html', sessionvar=session, channel=channel, stats=stats)
#     else:
#         return redirect(url_for('login'))

# create a test api route
@app.route('/api/getstat/<int:channel_id>', methods=['POST'])
def get_stat_api(channel_id):
    request_json = request.get_json()
    if request_json['req_type'] == "default":
        output = stat_functions_edited.get_default(channel_id)
        return flask.jsonify(output)
    elif request_json['req_type'] == "videos":
        time_range = request_json['time_range']
        # print('timedate changed to:', time_range)
        output = stat_functions_edited.get_videos(channel_id,time_range)
        return flask.jsonify(output)
    elif request_json['req_type'] == "subs":
        time_range = request_json['time_range']
        # print('timedate changed to:', time_range)
        output = stat_functions_edited.get_subscribers(channel_id,time_range)
        return flask.jsonify(output)
    elif request_json['req_type'] == "likes":
        time_range = request_json['time_range']
        print('timedate changed to:', time_range)
        output = stat_functions_edited.get_likes_stats(channel_id,time_range)
    #     return flask.jsonify(output)
    # elif request_json['req_type'] == "avd":
    #     time_range = request_json['time_range']
    #     print('timedate changed to:', time_range)
    #     output = stat_functions_edited.get_average_view_duration_stats(channel_id,time_range)
    #     return flask.jsonify(output)
    return "nonoe"

# page to edit channel details
@app.route('/channels/edit/<int:channel_id>', methods=['GET', 'POST'])
def edit_channel(channel_id):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            msg = None
            # get channel details to show in the form
            channel = cmsobj_db.get_channel(channel_id)
            
            # checking if channel has credentials
            if "temp_channel_name" in session:
                # accounting for it linked account does not have a youtube channel
                # remove credentials as a precaution
                if session["temp_channel_name"] == "No channel found":
                    msg = "Linked google account does not a have a youtube channel"
                    session.pop("temp_channel_name")
                    if "addcredentials" in session:
                        session.pop("addcredentials")
                else:
                    channel_name = session["temp_channel_name"]
                    # check if channel name matches the linked youtube channel
                    # if not then remove credentials
                    if channel_name != channel[1]:
                        msg = "Channel name does not match linked youtube channel"
                        session.pop("temp_channel_name")
                        if "addcredentials" in session:
                            session.pop("addcredentials")

            # get list of all creators
            creator = cmsobj_db.get_users_by_role(USER_TYPE_CREATOR)
            # get list of all editors
            editor = cmsobj_db.get_users_by_role(USER_TYPE_EDITOR)
            # get list of all ops
            ops = cmsobj_db.get_users_by_role(USER_TYPE_OPS)
            # get list of all managers
            manager = cmsobj_db.get_users_by_role(USER_TYPE_MANAGER)

            # check if request is POST then considered api request
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # call external function to edit channel details
                result = cmsobj_db.edit_channel(request.form.to_dict(), author)
                # if result is not True then return the result
                if result!=True:
                    return render_template('edit_channel.html', channel=channel, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg=result)
                # if 'addcredentials' in session then link the channel
                if 'addcredentials' in session:
                    # print("linking channel")
                    linkres = link_channel(channel_id)
                    if linkres!=True:
                        return linkres
                # if result is True then redirect to view all channels page
                return redirect(url_for('view_all_channels'))
            
            else:
                # get the channel details
                return render_template('edit_channel.html', channel=channel, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg = msg)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to add channels
@app.route('/channels/add', methods=['GET', 'POST'])
def add_channel():
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            msg = None
            channel_name = None

            # check if 'temp_channel_name' in session then store it in channel_name
            if "temp_channel_name" in session:
                # accounting for it linked account does not have a youtube channel
                # remove credentials as a precaution
                if session["temp_channel_name"] == "No channel found":
                    msg = "Linked google account does not a have a youtube channel"
                    if "addcredentials" in session:
                        session.pop("addcredentials")
                else:
                    channel_name = session["temp_channel_name"]
            
            # get list of all creators to show in the dropdown
            creator = cmsobj_db.get_users_by_role(USER_TYPE_CREATOR)
            # get list of all editors to show in the dropdown
            editor = cmsobj_db.get_users_by_role(USER_TYPE_EDITOR)
            # get list of all ops to show in the dropdown
            ops = cmsobj_db.get_users_by_role(USER_TYPE_OPS)
            # get list of all managers to show in the dropdown
            manager = cmsobj_db.get_users_by_role(USER_TYPE_MANAGER)
            
            # check if request is POST then considered api request
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # remove 'temp_channel_name' from session
                if "temp_channel_name" in session:
                    session.pop("temp_channel_name")
                # call external function to add channel
                channel_id = cmsobj_db.add_channel(request.form.to_dict(), author)
                # if result is not True then return the result
                if type(channel_id)!=int:
                    return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg=channel_id)
                elif type(channel_id)==int:
                    # if 'addcredentials' in session then link the channel
                    if "addcredentials" in session:
                        result = link_channel(channel_id)
                        if result!=True:
                            return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg=result)
                        else:
                            return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg="Channel added and linked Successfully")
                    else:
                        return render_template('add_channel.html', channel_name=None, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg="Channel added Successfully")
            return render_template('add_channel.html', channel_name=channel_name, creators=creator, editors=editor, opss=ops, managers=manager, status=channel_enumeration.channelstatus, platform=channel_enumeration.platform_names, msg=msg)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to link channel
@app.route('/channels/link/<int:channel_id>', methods=['GET','POST'])
def link_channel(channel_id):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            # check if request is POST then considered api request
            if request.method == 'POST':
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                # check if 'addcredentials' in session then store it in tokens
                if 'addcredentials' not in session:
                    return "No credentials found"
                else:
                    tokens = json.dumps(session['addcredentials'])
                    # remove 'addcredentials' from session
                    session.pop('addcredentials')
                    # call external function to link channel
                    result = cmsobj_db.link_channel(channel_id=channel_id, token=tokens, author=author)
                    # return the result
                    if result!=True:
                        return result
                    else:
                        return True
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to unlink channel
@app.route('/channels/unlink/<int:channel_id>')
def unlink_channel(channel_id):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            # check if request is POST then considered api request
            # print("unlinking channel")
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # print("unlinking channel2")
            # call external function to unlink channel
            result = cmsobj_db.unlink_channel(channel_id, author)
            # return value based on the result
            if result!=True:
                return result
            elif result == True:
                return redirect(request.referrer)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

# page to view a channel's details
@app.route('/view/<int:channel_id>')
def view_single_channel(channel_id):
    # check for login session
    if session.get('loggedin'):
        # get the channel details
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

# page to add videos to a channel
@app.route('/view/<int:channel_id>/add_video', methods=['GET', 'POST'])
def add_video(channel_id):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin, manager, ops or creator
        if session["user_type"] not in [USER_TYPE_ADMIN, USER_TYPE_MANAGER, USER_TYPE_OPS, USER_TYPE_CREATOR]:
            return "You are not authorized to add videos"
        # get the channel details
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to the channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        # check if request is POST then considered api request
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # call external function to add video
            result = cmsobj_db.add_video(request.form.to_dict(), author)
            # return value based on the result
            if result!=True:
                return render_template('add_video.html', sessionvar=session, channel=channel, msg=result)
            else:
                return render_template('add_video.html', sessionvar=session, channel=channel, msg="Video added Successfully")
        else:
            return render_template('add_video.html', sessionvar=session, channel=channel)
    else:
        return redirect(url_for('login'))

# page to update video status
@app.route('/update', methods=['GET', 'POST'])
def update_status():
    # check for login session
    if session.get('loggedin'):
        author = {
            'user_id': session['user_id'],
            'user_type': session['user_type']
        }
        # call external function to update video status
        result = cmsobj_db.set_video_status(request.form.to_dict(), author)
        # return value based on the result
        if result!=True:
            return result
        # return "you updated"
        return redirect(request.referrer)
    else:
        return redirect(url_for('login'))

# 
@app.route('/edit/video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    # check for login session
    if session.get('loggedin'):
        # get video details
        video = cmsobj_db.get_video(video_id)
        # get channel id and details
        channel_id = video[4]
        channel = cmsobj_db.get_channel(channel_id)
        # check if user is linked to channel
        if extra_functions.check_if_in_channel(session['user_type'], session['user_id'], channel) != True:
            return "You are not authorized to view this page"
        video = cmsobj_db.get_video(video_id)
        finalvidlist = list(video)
        for i in range(5,8):
            finalvidlist[i] = extra_functions.epoch_to_string(finalvidlist[i], 'date')
            # print(finalvidlist[i])
        # check if request is POST then considered api request
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # storing form data as dictionary to edit beforehand
            passreq = request.form.to_dict()
            # edit all timestamps from string to epoch
            passreq['shoot_timestamp'] = extra_functions.string_to_epoch(passreq['shoot_timestamp'])
            passreq['edit_timestamp'] = extra_functions.string_to_epoch(passreq['edit_timestamp'])
            passreq['upload_timestamp'] = extra_functions.string_to_epoch(passreq['upload_timestamp'])
            # call external function to edit video
            result = cmsobj_db.edit_video(passreq, author)
            # return value based on the result
            if result!=True:
                return render_template('edit_video.html', channel=channel, sessionvar=session, video=finalvidlist, msg=result)
            else:
                return redirect(url_for('view_single_channel', channel_id=request.form['channel_id']))
        else:
            
            return render_template('edit_video.html', channel=channel, sessionvar=session, video=finalvidlist)
    else:
        return redirect(url_for('login'))

# page to display all logs
@app.route('/logs/p=<int:pagenum>')
def get_logs(pagenum):
    # check for login session
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            # call external function to get logs and total number of logs
            output = cmsobj_db.get_logs_by_page(pagenum-1)
            # get logs and number of pages
            logs = output[0]
            number_of_pages = math.ceil(output[1]/50)
            # make a list to store logs
            final_logs = []
            # make a dictionary to store user details
            final_user_list = {}
            # get all users
            users = cmsobj_db.get_users(author=author)
            # add logs to final_logs list and convert dates from epoch to string
            for log in logs:
                final_logs.append([log[0], log[1], extra_functions.epoch_to_string(log[2], 'datetime'), ast.literal_eval(log[3].replace('null', 'None'))])
            # add users to final_user_list dictionary
            for user in list(users):
                final_user_list[user[0]] = [user[1], user[2]]
            return render_template('view_logs.html', logs=final_logs, users=final_user_list, action=general_log_enumeration.log_type, pagenum=pagenum, number_of_pages=number_of_pages)
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
        prompt='consent',
        access_type='offline',
        include_granted_scopes='true')
    session['state'] = state
    session['return_url'] = flask.request.referrer
    return redirect(auth_url)

# Oauth page 2
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    auth_response = flask.request.url
    flow.fetch_token(authorization_response=auth_response)
    
    credentials = flow.credentials
    youtube = build('youtube', 'v3', credentials=credentials)
    request1 = youtube.channels().list(
        part="snippet",
        mine=True
    )
    response = request1.execute()
    # print("RESPONSE:_")
    # print(response)
    if 'items' in response:
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

@app.route('/bulk_import/<int:channel_id>', methods=['GET','POST'])
def import_file(channel_id):
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            # get channel information
            channel = cmsobj_db.get_channel(channel_id)
            # check if request is POST then considered api request
            if request.method == 'POST':
                # check if 'file' in request files
                if 'file' not in request.files:
                    flash('No file provided')
                    return redirect(request.url)
                file = request.files['file']
                # check for empty file
                if file.filename == '':
                    flash("No file provided")
                    return redirect(request.url)
                # check if file is valid
                if file and file.filename.split('.')[1] in ALLOWED_EXTENSIONS:
                    # save file and filename
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # check if file is csv
                    if file.filename.split('.')[1] == "csv":
                        file_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        # get csv list
                        csv_list = handle_csv(file_url)
                        # format csv lsit for displaying
                        output = check_n_format_csv(csv_list)
                        # if output is a string then return error
                        if type(output) == str:
                            return "error: "+output
                        # get all channels
                        # print(csv_list)
                        return render_template('view_csv.html', csv_list=output, video_status=video_enumeration.vidstatus, file_url=file_url, channel_id=channel_id)
                else:
                    return "Invalid file"
            return render_template('import_page.html',channel=channel)
        else:
            return "You are not authorized to view this page"
    else:
        return redirect(url_for('login'))

@app.route('/import_csv', methods=['POST'])
def import_via_csv():
    if session.get('loggedin'):
        # check if user is admin
        if session['user_type'] == USER_TYPE_ADMIN:
            request_data = request.form.to_dict()
            channel_id = int(request_data['channel_id'])
            file_url = request_data['file_url']
            csv_list = handle_csv(file_url)
            output = check_n_format_csv(csv_list, import_format=True)
            # print(output[1])
            if type(output) == str:
                return "error: "+output
            else:
                author = {
                    'user_id': session['user_id'],
                    'user_type': session['user_type']
                }
                result = cmsobj_db.add_videos_bulk(output, channel_id, author)
                if result!=True:
                    return result
                else:
                    return redirect(url_for('view_single_channel', channel_id=channel_id))
        else:
            return "You are not authorized to access this function"
    else:
        return redirect(url_for('login'))
    
@app.route('/user_customise', methods=['GET', 'POST'])
def user_customise():
    if session.get('loggedin'):
        user_id = session['user_id']
        user = cmsobj_db.get_user(user_id)
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = cmsobj_db.edit_self(request.form.to_dict(), author)
            if result != True:
                return render_template('edit_self.html', sessionvar=session, user=user, msg=result)
            else:
                return redirect(url_for('dashboard'))
        return render_template('edit_self.html', sessionvar=session, user=user)
    else:
        return redirect(url_for('login'))

@app.route('/get_data_for_cache', methods=['POST'])
def get_data_for_cache():
    if session.get('loggedin'):
        if session['user_type'] == USER_TYPE_ADMIN:
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            channels_list = cmsobj_db.get_channels()
            # print(channels_list)
            users_list = cmsobj_db.get_users(author=author)
            return json.dumps({
                'success': True,
                'channels': channels_list,
                'users': users_list
            })
        else:
            return json.dumps({
                'success': False
            })
    else:
        return json.dumps({
            'success': False
        })

@app.route("/shutdown", methods=['GET'])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    try:
        app.run(debug=True, host="localhost",port=2077)
    except KeyboardInterrupt:
        print("Shutting down server")