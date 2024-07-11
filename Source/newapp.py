# Import necessary modules
import json
import extrafunc
import csv_functions
import stat_functions
from external_function import VidSchool
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
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
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
# Initialize VidSchool object with database connection parameters
vidschool = VidSchool(host, username, password, dbname)

# Set a secret key for session management
app.secret_key = 'your secret key'

@app.route('/')
def base():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if POST request with 'user_email' and 'password' in form data
    if request.method == 'POST' and 'user_email' in request.form and 'password' in request.form:       
        user_email = request.form['user_email']                                                        
        password = request.form['password']                                                            
        # Call external function to validate user credentials
        valid = vidschool.login_user(user_email, password)
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
        if session['user_type'] == 0:
            # return "Admin Dashboard"
            return render_template('dashboard.html', sessionvar=session)
        elif session['user_type'] >= 1:
            channellist = vidschool.get_channels_by_user(session['user_id'], session['user_type'])
            # return "Manager Dashboard"
            return render_template('dashboard.html', sessionvar=session, channels=channellist)
    else:
        return redirect(url_for('login'))

@app.route('/view/<int:channel_id>')
def view_channel(channel_id):
    if session.get('loggedin'):
        channels = vidschool.get_channel(channel_id)
        # print(channels)
        videos = vidschool.get_videos_by_channel(channel_id)
        # print(videos)
        users = {
            channels[3] : vidschool.get_user(channels[3])[1],
            channels[4] : vidschool.get_user(channels[4])[1],
            channels[5] : vidschool.get_user(channels[5])[1],
            channels[6] : vidschool.get_user(channels[6])[1]
            
        }
        return render_template('view_channel.html', sessionvar=session,channel=channels, videos=videos, users=users)
    else:
        return redirect(url_for('login'))

@app.route('/update', methods=['GET', 'POST'])
def update_status():
    if session.get('loggedin'):
        author = {
            'user_id': session['user_id'],
            'user_type': session['user_type']
        }
        result = vidschool.set_video_status(request.form.to_dict(), author)
        if result!=True:
            return result
        # return "you updated"
        return flask.redirect(request.referrer)
    else:
        return redirect(url_for('login'))

@app.route('/delete/video/<int:video_id>')
def delete_video(video_id):
    if session.get('loggedin'):
        author = {
            'user_id': session['user_id'],
            'user_type': session['user_type']
        }
        result = vidschool.set_delete_video(video_id=video_id, author=author)
        print("result: ", result)
        if result!=True:
            return result
        return flask.redirect(request.referrer)
    else:
        return redirect(url_for('login'))

@app.route('/edit/video/<int:video_id>', methods=['GET', 'POST'])
def edit_video(video_id):
    if session.get('loggedin'):
        if request.method == 'POST':
            print(request.form.to_dict())
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = vidschool.update_video(request.form.to_dict(), author)
            if result!=True:
                return result
            return redirect(url_for('view_channel', channel_id=request.form['channel_id']))
        video = vidschool.get_video(video_id)
        return render_template('edit_video.html', sessionvar=session, video=video)
    else:
        return redirect(url_for('login'))

@app.route('/view/<int:channel_id>/add_video', methods=['GET', 'POST'])
def add_video(channel_id):
    if session.get('loggedin'):
        if session["user_type"] == 3:
            return "You are not authorized to add videos"
        if request.method == 'POST':
            author = {
                'user_id': session['user_id'],
                'user_type': session['user_type']
            }
            result = vidschool.add_video(request.form.to_dict(), author)
            if result!=True:
                return result
            else:
                return render_template('add_video.html', sessionvar=session, channel_id=channel_id, msg="Video added Successfully")
            # return redirect(url_for('view_channel', channel_id=channel_id))
        return render_template('add_video.html', sessionvar=session, channel_id=channel_id)
    else:
        return redirect(url_for('login'))

# Main entry point of the application
if __name__ == '__main__':
    vidschool.setupdb()                                            # Setup any necessary components from extfun module
    app.run(debug=True, port=8089,host='localhost')                                            # Run the Flask application in debug mode
