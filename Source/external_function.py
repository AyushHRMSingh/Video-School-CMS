import ast
import json
import bcrypt
import mysql.connector
import time

import mysql.connector.errorcode
import api_functions as api_functions
import extra_functions 
from type_vars import *

class VidSchool:
    # constructor function
    def __init__(self, dbhost, dbusername, dbpassword, dbname):
        # getting database object
        connected = False
        while not connected:
            try:
                self.dbconnect = mysql.connector.connect(
                    host = dbhost,
                    user = dbusername,
                    password = dbpassword
                )
                self.cursor = self.dbconnect.cursor()
                self.dbname = dbname
                self.sqlcommands = [
                    "USE  {}".format(dbname),
                ]

                if self.dbconnect.is_connected():
                    print("Connected to database")
                    connected = True
                    self.select_db()
                VidSchool.credentialpool = {}
                VidSchool.start_credential_pool(self)
            except Exception as e:
                print("Error connecting to database: ", e)
                print('Retrying in 5 seconds')
                time.sleep(5)
    
    # destructor function
    def __del__(self):
        if self.dbconnect.is_connected():
            self.dbconnect.close()
            print("Disconnected from database")

    # hashing and salting password for security with bcrypt library
    def hash_password(self, password):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')

    # Select the database to be used
    def select_db(self):
        for command in self.sqlcommands:
            self.cursor.execute(command)
            self.dbconnect.commit()
        print("Setup complete")

    @staticmethod
    def start_credential_pool(self):
        sql = "SELECT * FROM Channel WHERE JSON_LENGTH(tokens) > 0;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        # add credentials to credential pool
        if result == []:
            print("No channels found")
            VidSchool.credentialpool = {}
            return False
        for i in list(result):
            cred = [i[8]]
            cred = ast.literal_eval(cred[0])
            VidSchool.credentialpool[i[0]] = cred
        print("Credential pool started")

        # # Refresh all access tokens
        for i in VidSchool.credentialpool:
            oldcred = VidSchool.credentialpool[i]
            # oldcred = ast.literal_eval(oldcred)
            VidSchool.credentialpool[i] = api_functions.refresh_token(oldcred)
        print("Credential pool refreshed")

    @staticmethod
    def check_credential_pool():
        for i in VidSchool.credentialpool:
            if VidSchool.credentialpool[i][1] > time.time():
                cred = VidSchool.credentialpool[i][0]
                # cred = ast.literal_eval(cred)
                VidSchool.credentialpool[i] = api_functions.refresh_token(cred)
        return True

    @staticmethod
    def get_credentials(channel_id):
        VidSchool.check_credential_pool()
        if channel_id not in VidSchool.credentialpool:
            print("Channel not found")
            return False
        # cred = ast.literal_eval(VidSchool.credentialpool[channel_id][0])
        cred = VidSchool.credentialpool[channel_id][0]
        return cred

    ### USER FUNCTIONS
    def add_user(self,request, author):
        # checks permission
        if author['user_type'] == USER_TYPE_ADMIN:
            # hash password for security
            hashpass = self.hash_password(request['user_email'])
            # executes SQL command
            sql = "INSERT INTO User (name, email, password, role, status) VALUES (%s, %s, %s, %s, 0)"
            val = (request['user_name'], request['user_email'], hashpass, request['user_type'])
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "User Already Exists"
            self.cursor.execute("SELECT ID FROM User WHERE email = %s AND password = %s", (request['user_email'], hashpass))
            user = self.cursor.fetchone()
            # Logging
            log_data = {
                "action": "add_user",
                "author_id": author['user_id'],
                "data" : {
                    "user_id": user[0],
                    "user_email": request['user_email'],
                    "user_type": request['user_type']
                }
            }
            self.log_action(1, log_data)
            return True
        else:
            return "You do not have permission to add users"

    # sets user to INACTIVE
    def delete_user( self, user_id, author):
        # checks permissions
        if author['user_type'] == USER_TYPE_ADMIN:
            user = self.get_user(user_id)
            if user[4] == USER_TYPE_ADMIN:
                return "You cannot delete the admin user"
            # executes SQL command
            sql = "UPDATE User SET status = 1 WHERE ID = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # Logging
            log_data = {
                "action": "delete_user",
                "author_id": author['user_id'],
                "data" : {
                    "user_id": user_id
                }
            }
            self.log_action(1, log_data)
            return True
        else:
            return "You do not have permission to delete this user"

    # function to get all users in the database
    def get_users(self, author):
        # checks permissions
        if author['user_type'] == USER_TYPE_ADMIN:
            # executes SQL command
            sql = "SELECT * FROM User"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        else:
            return "You do not have permission to view this data"
    
    def get_users_by_role(self, user_type):
        # checks permissions
        # executes SQL command
        sql = "SELECT * FROM User WHERE role = %s and status = 0"
        val = (user_type,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    # function to get a specific user from the database
    def get_user(self, user_id):
        # executes SQL command
        sql = "SELECT * FROM User WHERE ID = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result
    
    # function to edit a user in the database
    def edit_user(self, request, author):
        # checks permissions
        if author['user_type'] == USER_TYPE_ADMIN:
            # stores default values from DB
            if int(request['user_type']) == USER_TYPE_ADMIN:
                return "You cannot edit the admin user"
            user_id = int(request['user_id'])
            defvalue = self.get_user(user_id)
            # sets values to default if None
            user_name = request['user_name'] if request['user_name'] != "" else defvalue[1]
            user_email = request['user_email'] if request['user_email'] != "" else defvalue[2]
            user_type = int(request['user_type']) if request['user_type'] != "" else defvalue[4]
            status = int(request['status']) if request['status'] != "" else defvalue[5]
            # executes SQL command
            sql = "UPDATE User SET name = %s, email = %s, role = %s, status = %s WHERE ID = %s"
            val = (user_name, user_email, user_type, status, user_id)
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "User Already Exists"
            # Logging
            log_data = {
                "action": "edit_user",
                "author_id": author['user_id'],
                "data": {
                    "user_id": user_id,
                    "user_email": user_email,
                    "user_type": user_type
                }
            }
            self.log_action(1, log_data)
            return True
        else:
            return {
                "error": "You do not have permission to edit this user"
            }

    ### VIDEO FUNCTIONS
    # function to add a video to the database
    def add_video(self, request, author):
        # checks user is higher permissions than ops
        video_title = request['video_title']
        channel_id = request['channel_id']
        if author['user_type'] in [USER_TYPE_ADMIN, USER_TYPE_MANAGER, USER_TYPE_OPS, USER_TYPE_CREATOR]:
            # executes SQL command
            sql = "INSERT INTO Video (title, channel_id, status) VALUES (%s, %s, 0)"
            val = (video_title, channel_id,)
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "Video Already Exists"
            # Logging
            log_data = {
                "action": "add_video",
                "author_id": author['user_id'],
                "data": {
                    "video_title": video_title,
                    "channel_id": channel_id,
                }
            }
            self.log_action(3, log_data)
            return True
        else:
            return {
                "error": "You do not have permission to add videos"+str(author['user_type'])
            }

    # function to update a video in the database
    def edit_video(self, request, author):
        if author['user_type'] in [USER_TYPE_ADMIN, USER_TYPE_MANAGER, USER_TYPE_OPS, USER_TYPE_CREATOR]:
            # stores values from DB as default
            video_id = int(request['video_id']) 
            defvalue = self.get_video(video_id)
            # if value is None, set to default value
            video_title = request['video_title'] if request['video_title'] != '' else defvalue[2]
            video_url = request['video_url'] if request['video_url'] != '' else defvalue[3]
            channel_id = int(request['channel_id']) if request['channel_id'] != '' else defvalue[4]
            shoot_timestamp = request['shoot_timestamp'] if request['shoot_timestamp'] != '' else defvalue[5]
            edit_timestamp = request['edit_timestamp'] if request['edit_timestamp'] != '' else defvalue[6]
            upload_timestamp = request['upload_timestamp'] if request['upload_timestamp'] != '' else defvalue[7]
            status = int(request['status']) if request['status'] != '' else defvalue[8]
            if 'comment' not in request:
                comment = ''
            else:
                comment = request['comment']
            # executes SQL command
        # executes SQL command
            sql = "UPDATE Video SET title = %s, url = %s,channel_id = %s, shoot_timestamp = %s, edit_timestamp = %s, upload_timestamp = %s, status = %s, comment = %s WHERE id = %s"
            val = (video_title, video_url, channel_id, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment, video_id)
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "Video Already Exists"
            # Logging
            log_data = {
                "action": "edit_video",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id,
                    "video_title": video_title,
                    "channel_id": channel_id,
                    "shoot_timestamp": shoot_timestamp,
                    "edit_timestamp": edit_timestamp,
                    "upload_timestamp": upload_timestamp,
                    "status": status
                }
            }
            self.log_action(3, log_data)
            return True
        else:
            return {
                "error": "You do not have permission to update this video"
            }

    # function to set the status of a video
    def set_video_status(self, request, author):
        video_id = int(request['video_id'])
        status = int(request["status"])
        if 'comment' not in request:
            comment = ''
        else:
            comment = request['comment']
        # checks different usertypes to check if action is permitted
        # creator
        if author['user_type'] == USER_TYPE_CREATOR:
            if status != 1:
                return {
                    "error": "You do not have permission to set that status"
                }
            sql = "UPDATE Video SET status = %s, comment = %s, shoot_timestamp=%s WHERE ID = %s"
            # executes SQL command
            val = (status, comment, time.time(), video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
        # editor
        elif author['user_type'] == USER_TYPE_EDITOR:
            if status != 2:
                return {
                    "error": "You do not have permission to set that status"
                }
            sql = "UPDATE Video SET status = %s, comment = %s, edit_timestamp=%s WHERE ID = %s"
            # executes SQL command
            val = (status, comment, time.time(), video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
        # operations
        elif author['user_type'] == USER_TYPE_OPS:
            # print("ops: ",status)
            if status not in [VIDEO_STATUS_UPLOADED, VIDEO_STATUS_TO_BE_REEDITED, VIDEO_STATUS_TO_BE_RESHOT]:
                # print("ops: ",status)
                return {
                    "error": "You do not have permission to set that status"
                }
            if status == VIDEO_STATUS_UPLOADED:
                url = request['url']
                sql = "UPDATE Video SET status = %s, comment = %s, url=%s, upload_timestamp=%s WHERE ID = %s"
                # executes SQL command
                val = (status, comment, url, time.time(), video_id,)
            else:
                sql = "UPDATE Video SET status = %s, comment = %s WHERE ID = %s"
                val = (status, comment, video_id,)    
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
        elif author['user_type'] in [USER_TYPE_MANAGER, USER_TYPE_ADMIN]:
            print("Manager or Admin")
        else:
            # return if invalid author
            return {
                "error": "INVALID AUTHOR"
            }
        # executes SQL command
        sql = "UPDATE Video SET status = %s, comment = %s WHERE ID = %s"
        # executes SQL command
        val = (status, comment, video_id,)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        # Logging
        log_data = {
            "action": "set_video_status",
            "author_id": author['user_id'],
            "data": {
                "video_id": video_id,
                "status": status,
                "comment": comment
            }
        }
        self.log_action(3, log_data)
        return True
    
    # function to delete a video from the database
    def set_delete_video(self, video_id, author):
        # checks that user is higher than ops
        if author['user_type'] <=2:
            # executes SQL command
            sql = "UPDATE Video SET status = 7 WHERE ID = %s"
            val = (video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # Logging
            log_data = {
                "action": "delete_video",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id
                }
            }
            self.log_action(3, log_data)
            return True
        else:
            return {
                "error": "You do not have permission to delete this video"
            }
    # function to get all videos from the database
    
    def get_videos(self):
        # executes SQL command
        sql = "SELECT * FROM Video"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # get videos by channel
    def get_videos_by_channel(self, channel_id):
        # executes SQL command
        sql = "SELECT * FROM Video WHERE channel_id = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    # function to get a specific video from the database
    def get_video(self, video_id):
        # executes SQL command
        sql = "SELECT * FROM Video WHERE ID = %s"
        val = (video_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result
    
    # function to add videos in bulk
    def add_videos_bulk(self, csv_list, channel_id, author):
        if author['user_type'] == USER_TYPE_ADMIN:
            # executes SQL command to add all videos in a single command
            sql = 'INSERT INTO Video (old_id, title, url, channel_id, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            insert_list = []
            for i in range(0, len(csv_list)):
                row = csv_list[i]
                old_id = row[0]
                title = row[1]
                url = row[2] if row[2] != '' else None
                shoot_timestamp = int(row[3]) if row[3] != '' else None
                edit_timestamp = int(row[4]) if row[4] != '' else None
                upload_timestamp = int(row[5]) if row[5] != '' else None
                comment = row[6] if row[6] != '' else None
                status = int(row[7]) if row[7] != '' else None
                insert_list.append((old_id, title, url, channel_id, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment))
            print(sql)
            try:
                self.cursor.executemany(sql, insert_list)
                self.dbconnect.commit()
                print("Videos added")
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "Video Already Exists"
            # Logging
            log_data = {
                "action": "add_videos",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                }
            }
            self.log_action(3, log_data)
            return True
        else:
            return {
                "error": "You do not have permission to add videos"
            }

    ### CHANNEL FUNCTIONS
    def add_channel(self, request, author):
        if author['user_type'] == USER_TYPE_ADMIN:
            # executes SQL command
            sql = "INSERT INTO Channel (name ,platform, creator_id, editor_id, manager_id, ops_id, status) VALUES (%s, %s, %s, %s, %s, %s, 0)"
            val = (request['channel_name'], int(request['platform']), int(request['creator_id']), int(request['editor_id']), int(request['manager_id']), int(request['ops_id']))
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "Channel Already Exists"
            # gets channel ID after adding
            sql = "SELECT ID FROM Channel WHERE name = %s AND platform = %s"
            val = (request['channel_name'], int(request['platform']))
            self.cursor.execute(sql, val)
            channel = self.cursor.fetchone()
            channel_id = channel[0]
            # Logging
            log_data = {  
                "action": "add_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "channel_name": request['channel_name'],
                    "platform": int(request['platform'])
                }
            }
            self.log_action(2, log_data)
            return channel_id
        else:
            return "You do not have permission to add channels"

    # function get user channels
    def get_channels_by_user(self, user_id, user_type):
        # check usertype and set sql command
        if user_type == USER_TYPE_CREATOR:
            sql = "SELECT * FROM Channel WHERE creator_id = %s"
        elif user_type == USER_TYPE_EDITOR:
            sql = "SELECT * FROM Channel WHERE editor_id = %s"
        elif user_type == USER_TYPE_OPS:
            sql = "SELECT * FROM Channel WHERE ops_id = %s"
        elif user_type == USER_TYPE_MANAGER:
            sql = "SELECT * FROM Channel WHERE manager_id = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    # function to delete a channel from the database
    def delete_channel(self, channel_id, author):
        # checks if user is admin
        if author['user_type'] == USER_TYPE_ADMIN:
            # executes SQL command
            sql = "UPDATE Channel SET status = 3 WHERE ID = %s"
            val = (channel_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # logging
            log_data = {
                "action": "delete_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id
                }
            }
            self.log_action(2, log_data)

    def link_channel(self, channel_id, token, author):
        if author['user_type'] == USER_TYPE_ADMIN:
            try:
            # print(jsontoken)
                # print("Linking channel")
                sql = "UPDATE Channel SET tokens = %s WHERE id=%s"
                val = (token, channel_id)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                log_data = {
                    "action": "link_channel",
                    "author_id": author['user_id'],
                    "data": {
                        "channel_id": channel_id,
                    }
                }
                self.log_action(2, log_data)
                VidSchool.start_credential_pool(self)
                return True
            except Exception as e:
                # print(e)
                return str(e)
        else:
            return "You do not have permission to link channels"

    def unlink_channel(self, channel_id, author):
        if author['user_type'] == 0:
            try:
                sql = "update channel set tokens=JSON_OBJECT() where id=%s"
                val = (channel_id,)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                log_data = {
                    "action": "unlink_channel",
                    "author_id": author['user_id'],
                    "data": {
                        "channel_id": channel_id,
                    }
                }
                self.log_action(2, log_data)
                VidSchool.start_credential_pool(self)
                return True
            except Exception as e:
                # print(e)
                return str(e)
        else:
            return "You do not have permission to unlink channels"

    # function to edit a channel in the database
    def edit_channel(self, request, author):
        # checks if user is admin
        if author['user_type'] == USER_TYPE_ADMIN:
            channel_id = request['channel_id']
            channel = self.get_channel(channel_id)
            channel_name = request['channel_name'] if request['channel_name'] != "" else channel[1]
            platform = int(request['platform']) if request['platform'] != "" else channel[2]
            creator_id = int(request['creator_id']) if request['creator_id'] != "" else channel[3]
            editor_id = int(request['editor_id']) if request['editor_id'] != "" else channel[4]
            manager_id = int(request['manager_id']) if request['manager_id'] != "" else channel[5]
            ops_id = int(request['ops_id']) if request['ops_id'] != "" else channel[6]
            status = int(request['status']) if request['status'] != "" else channel[7]
            # executes SQL command
            sql = "UPDATE Channel SET name = %s, platform = %s, creator_id = %s, editor_id = %s, manager_id = %s, ops_id = %s, status = %s WHERE ID = %s"
            val = (channel_name, platform, creator_id, editor_id, manager_id, ops_id, status, channel_id)
            try:
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            except mysql.connector.IntegrityError as err:
                if err.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
                    return "Channel Already Exists"
            # logging
            log_data = {
                "action": "edit_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "platform": platform,
                    "creator_id": creator_id,
                    "editor_id": editor_id,
                    "manager_id": manager_id,
                    "ops_id": ops_id,
                    "status": status
                }
            }
            self.log_action(2, log_data)
            return True
        else:
            return "You do not have permission to edit this channel"

    # function to update the status of a channel
    def update_channel_status(self, channel_id, status, author):
        # checks if user is admin
        if author['user_type'] == USER_TYPE_ADMIN:
            # executes SQL command
            sql = "UPDATE Channel SET status = %s WHERE ID = %s"
            val = (status, channel_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # logging
            log_data = {
                "action": "update_channel_status",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "status": status
                }
            }
            self.log_action(2, log_data)
    
    # gets all channels from the database
    def get_channels(self):
        # executes SQL command
        sql = "SELECT * FROM Channel;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
    
    # gets a specific channel from the database
    def get_channel(self, channel_id):
        # executes SQL command
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result

    # function to login a user and return user details if successfull
    def login_user(self, user_email, password):
        # executes SQL command
        sql = "SELECT * FROM User WHERE email = %s AND status = 0"
        val = (user_email,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        # User not found
        if result == None:
            return {
                "success": False,
                "error": "User does not exist"
            }
        elif result[5] == USER_STATUS_ACTIVE: 
            # checks if password is correct
            if bcrypt.checkpw(password.encode('utf-8'), result[3].encode('utf-8')):
                # Logging
                log_data = {
                    "action": "login",
                    "data": {
                        "user_id": result[0],
                        "user_email": user_email,
                        "login_time": int( time.time() )
                    }
                }
                self.log_action(0, log_data)
                # returns infor for session storage
                return {
                    "success": True,
                    "user_id": result[0],
                    "user_name": result[1],
                    "user_email": result[2],
                    "user_type": result[4],
                }
        # if all else fails
        else:
            return {
                "success": False,
                "error": "invalid database?"
            }
        
    # log every action
    def log_action(self, log_type, log_data, log_time = int( time.time() )):
        # converts log_data to JSON
        log_data = json.dumps(log_data)
        # executes SQL command
        sql = "INSERT INTO Log_Table (type, date, data) VALUES (%s, %s, %s)"
        val = (log_type, log_time, log_data)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    # get all logs
    def get_logs(self):
        # executes SQL command
        sql = "SELECT * FROM Log_Table"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # sql = "SELECT COUNT(*) FROM Log_Table"
    #     self.cursor.execute(sql)
    #     result = self.cursor.fetchone()
    #     row_num = result[0]
    #     print(row_num)
    #     sql = "SELECT * FROM Log_Table ORDER BY date DESC LIMIT 100 OFFSET %s"
    #     val = (row_num-(page*100),)
    #     self.cursor.execute(sql, val)
    #     result = self.cursor.fetchall()
    #     print(result)
    #     return result

    def get_logs_by_page(self, page):
        sql = "SELECT COUNT(*) FROM Log_Table"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        row_num = result[0]
        print(row_num)
        sql2 = "SELECT * FROM Log_Table ORDER BY id DESC LIMIT 100 OFFSET %s"
        val = ((page*100),)
        self.cursor.execute(sql2, val)
        result2 = self.cursor.fetchall()
        print(sql2, val)
        # print(result2)
        return [result2, row_num]
    
    ## TEST FUNCTIONS FOR DEBUGGING
    # Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
    def clearpro(self):
        self.cursor.execute("DROP DATABASE {}".format(self.dbname))
        self.dbconnect.commit()
        print("Database cleared")