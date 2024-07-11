import ast
import json
import bcrypt
import mysql.connector
import time
import api_functions as api_functions
import extrafunc

class VidSchool:
    # constructor function
    def __init__(self, dbhost, dbusername, dbpassword, dbname):
        print("Object initialized NOW")
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
        print("Connected to database")
        if self.dbconnect.is_connected():
            self.setupdb()
        VidSchool.credentialpool = {}
        VidSchool.start_credential_pool(self)
    
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

    # Setup the database with the proper schema
    def setupdb(self):
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
            return False
        for i in result:
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

    # def refresh_credential_pool(self):
    #     for i in VidSchool.credentialpool:
    #         VidSchool.credentialpool[i] = apifunc.refresh_token(VidSchool.credentialpool[i])

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
    # function to add a user to the database ONLY FOR ADMIN
    def add_user(self, user_name,user_email, password, user_type, author):
        # checks permission
        if author['user_type'] == 0:
            # hash password
            hashpass = self.hash_password(password)
            # executes SQL command
            sql = "INSERT INTO User (name, email, password, role, status) VALUES (%s, %s, %s, %s, 0)"
            val = (user_name, user_email, hashpass, user_type)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            self.cursor.execute("SELECT ID FROM User WHERE email = %s AND password = %s", (user_email, hashpass))
            user = self.cursor.fetchone()
            # Logging
            log_data = {
                "action": "add_user",
                "author_id": author['user_id'],
                "data" : {
                    "user_id": user[0],
                    "user_email": user_email,
                    "user_type": user_type
                }
            }
            self.log_action(1, log_data)

    # sets user to INACTIVE
    def delete_user( self, user_id, author):
        # checks permissions
        if author['user_type'] == 0:
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

    # function to get all users in the database
    def get_users(self, author):
        # checks permissions
        if author['user_type'] == 0:
            # executes SQL command
            sql = "SELECT * FROM User"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        else:
            return {
                "error": "You do not have permission to view this data"
            }
    
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
    def edit_user(self, user_name, user_id, user_email, user_type, status, author):
        # checks permissions
        if author['user_type'] == 0:
            # stores default values from DB
            defvalue = self.get_user(user_id)
            # sets values to default if None
            user_name = user_name if user_name != None else defvalue[1]
            user_email = user_email if user_email != None else defvalue[2]
            user_type = user_type if user_type != None else defvalue[4]
            status = status if status != None else defvalue[5]
            # executes SQL command
            sql = "UPDATE User SET name = %s, email = %s, role = %s, status = %s WHERE ID = %s"
            val = (user_name, user_email, user_type, status, user_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        if author['user_type'] <= 2 or author['user_type'] == 4:
            # executes SQL command
            sql = "INSERT INTO Video (title, channel_id, status) VALUES (%s, %s, 0)"
            val = (video_title, channel_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
                "error": "You do not have permission to add videos"
            }

    def add_videos_bulk(self, videos, channel_id, author):
        if author['user_type'] == 0:
            for video in videos:
                sql = "INSERT INTO Video (old_id, title, url, channel_id, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (video[0], video[1], video[2], channel_id, video[3], video[4], video[5], video[6], video[7])
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
            log_data = {
                "action": "add_videos_bulk",
                "author_id": author['user_id'],
                "data": {
                    "numebr_of_videos": len(videos)-1,
                    "channel_id": channel_id
                }
            }

    # function to update a video in the database
    def update_video(self, request, author):
        if author['user_type'] <= 2 or author['user_type'] == 4:
            # stores values from DB as default
            video_id = int(request['video_id']) 
            video_title = request['video_title']
            video_url = request['video_url']
            channel_id = int(request['channel_id'])
            shoot_timestamp = request['shoot_timestamp']
            edit_timestamp = request['edit_timestamp']
            upload_timestamp = request['upload_timestamp']
            status = int(request['status'])
            comment = request['comment']
            
            defvalue = self.get_video(video_id)
            # if value is None, set to default value
            video_title = video_title if video_title != '' else defvalue[2]
            video_url = video_url if video_url != '' else defvalue[3]
            channel_id = channel_id if channel_id != '' else defvalue[3]
            shoot_timestamp = shoot_timestamp if shoot_timestamp != '' else defvalue[4]
            edit_timestamp = edit_timestamp if edit_timestamp != '' else defvalue[5]
            upload_timestamp = upload_timestamp if upload_timestamp != '' else defvalue[6]
            status = status if status != '' else defvalue[7]
            comment = comment if comment != '' else defvalue[8]
            # executes SQL command
        # executes SQL command
            sql = "UPDATE Video SET title = %s, url = %s,channel_id = %s, shoot_timestamp = %s, edit_timestamp = %s, upload_timestamp = %s, status = %s, comment = %s WHERE id = %s"
            val = (video_title, video_url, channel_id, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment, video_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # Logging
            log_data = {
                "action": "update_video",
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
        comment = request['comment']
        # checks if comment is set
        if comment == '':
            comment = None
        # checks different usertypes to check if action is permitted
        # creator
        print(author['user_type']," : ",status)
        if author['user_type'] == 4:
            if status != 1:
                return {
                    "error": "You do not have permission to set that status"
                }
        # editor
        elif author['user_type'] == 3:
            if status != 2:
                return {
                    "error": "You do not have permission to set that status"
                }
        # operations
        elif author['user_type'] == 2:
            if status != 3:
                return {
                    "error": "You do not have permission to set that status"
                }
        elif author['user_type'] == 1 or author['user_type'] == 0:
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
                "status": status
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
    
    # function to get videos assigned to a user
    def get_videos_by_user(self, user_id, user_type):
        # creator
        if user_type == 4:
            # executes SQL command
            sql = "SELECT ID FROM Channel WHERE creator_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
        # editor
        elif user_type == 3:
            # executes SQL command
            sql = "SELECT ID FROM Channel WHERE editor_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
        # operations
        elif user_type == 2:
            # executes SQL command
            sql = "SELECT ID FROM Channel WHERE ops_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
        elif user_type == 1:
            # executes SQL command
            sql = "SELECT ID FROM Channel WHERE manager_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
            print("channels:-")
            print(Channels)
        else:
            return {
                "error": "INVALID USER TYPE"
            }
        Videos = []
        for i in Channels:
            sql = "SELECT * FROM Video WHERE channel_id = %s"
            val = (i[0],)
            self.cursor.execute(sql, val)
            result = self.cursor.fetchall()
            if result != []:
                Videos+=result
        return Videos

    def set_video_uploaded(self, video_id, url,author):
        if author['user_type'] <= 2:
            sql = "UPDATE Video SET status = 3, url = %s WHERE ID = %s"
            val = (url, video_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action":"upload video",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id,
                    "url": url
                }
            }
            self.log_action(3, log_data)
        else:
            return {
                "error": "You do not have permission to upload videos"
            }

    def get_relevant_videos(self, user_id,user_type):
        if user_type == 4:
            sql = "SELECT * FROM Channel WHERE creator_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
            video = []
            for I in Channels:
                sql = "SELECT * FROM Video WHERE channel_id = %s AND (status = 0 OR status = 3)"
                val = (I[0],)
                self.cursor.execute(sql, val)
                result = self.cursor.fetchall()
                video.append(result)
        elif user_type == 3:
            sql = "SELECT * FROM Channel WHERE editor_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
            video = []
            for I in Channels:
                sql = "SELECT * FROM Video WHERE channel_id = %s AND (status = 1 OR status = 4)"
                val = (I[0],)
                self.cursor.execute(sql, val)
                result = self.cursor.fetchall()
                video.append(result)
        elif user_type == 2:
            sql = "SELECT * FROM Channel WHERE ops_id = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            Channels = self.cursor.fetchall()
            if Channels == []:
                return False
            video = []
            for I in Channels:
                sql = "SELECT * FROM Video WHERE channel_id = %s AND status = 2"
                val = (I[0],)
                self.cursor.execute(sql, val)
                result = self.cursor.fetchall()
                video.append(result)

    # get videos by channel
    def get_videos_by_channel(self, channel_id):
        # executes SQL command
        sql = "SELECT * FROM Video WHERE channel_id = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    # get video by role
    def get_videos(self, author):
        # creator
        if author['user_type'] == 4:
            # executes SQL command
            sql = "SELECT * FROM Video WHERE status = 0 OR status = 3"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        # editor
        elif author['user_type'] == 3:
            # executes SQL command
            sql = "SELECT * FROM Video WHERE status = 1 OR status = 4"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        # operations
        elif author['user_type'] == 2:
            # executes SQL command
            sql = "SELECT * FROM Video WHERE status = 3"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        # manager and admin
        elif author['user_type'] == 1 or author['user_type'] == 0:
            # executes SQL command
            sql = "SELECT * FROM Video"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        else:
            return {
                "error":"INVALID AUTHOR"
            }

    # function to get a specific video from the database
    def get_video(self, video_id):
        # executes SQL command
        sql = "SELECT * FROM Video WHERE ID = %s"
        val = (video_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result
    
    ### CHANNEL FUNCTIONS
    def add_channel(self, channel_name, platform, creator_id, editor_id, manager_id, ops_id, author):
        # checks if user is admin
        if author['user_type'] == 0:
            # executes SQL command
            sql = "INSERT INTO Channel (name ,platform, creator_id, editor_id, manager_id, ops_id, status) VALUES (%s, %s, %s, %s, %s, %s, 0)"
            val = (channel_name, platform, creator_id, editor_id, manager_id, ops_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # gets channel ID after adding
            sql = "SELECT ID FROM Channel WHERE name = %s AND platform = %s"
            val = (channel_name, platform)
            self.cursor.execute(sql, val)
            channel = self.cursor.fetchone()
            channel_id = channel[0]
            # Logging
            log_data = {  
                "action": "add_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "platform": platform
                }
            }
            self.log_action(2, log_data)
            return channel_id

    # function get user channels
    def get_channels_by_user(self, user_id, user_type):
        # check usertype and set sql command
        if user_type == 4:
            sql = "SELECT * FROM Channel WHERE creator_id = %s"
        elif user_type == 3:
            sql = "SELECT * FROM Channel WHERE editor_id = %s"
        elif user_type == 2:
            sql = "SELECT * FROM Channel WHERE ops_id = %s"
        elif user_type == 1:
            sql = "SELECT * FROM Channel WHERE manager_id = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        return result

    # function to delete a channel from the database
    def delete_channel(self, channel_id, author):
        # checks if user is admin
        if author['user_type'] == 0:
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
        if author['user_type'] == 0:
            try:
            # print(jsontoken)
                print("Linking channel")
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
            except Exception as e:
                print(e)
                return {
                    "error": str(e)
                }
        else:
            return {
                "error": "You do not have permission to link channels"
            }

    # function to edit a channel in the database
    def edit_channel(self, channel_id, channel_name, platform, creator_id, editor_id, manager_id, ops_id, status, author):
        # checks if user is admin
        if author['user_type'] == 0:
            # stores default values from DB
            defvalue = self.get_channel(channel_id)
            # sets values to default if None
            channel_name = channel_name if channel_name != None else defvalue[1]
            platform = platform if platform != None else defvalue[3]
            creator_id = creator_id if creator_id != None else defvalue[4]
            editor_id = editor_id if editor_id != None else defvalue[5]
            manager_id = manager_id if manager_id != None else defvalue[6]
            ops_id = ops_id if ops_id != None else defvalue[7]
            status = status if status != None else defvalue[8]
            # executes SQL command
            sql = "UPDATE Channel SET name = %s, platform = %s, creator_id = %s, editor_id = %s, manager_id = %s, ops_id = %s, status = %s WHERE ID = %s"
            val = (channel_name, platform, creator_id, editor_id, manager_id, ops_id, status, channel_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # logging
            log_data = {
                "action": "edit_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "channel_name": channel_name,
                    "platform": platform
                }
            }
            self.log_action(2, log_data)

    # function to update the status of a channel
    def update_channel_status(self, channel_id, status, author):
        # checks if user is admin
        if author['user_type'] == 0:
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

    # function to add a user to a channel with a specific role
    def assign_user_to_channel(self, user_id, channel_id, user_type, author):
        # creator
        if user_type == '4':
            # sets SQL command
            sql = "UPDATE Channel SET creator_id = %s WHERE ID = %s"
        # editor
        elif user_type == '3':
            # sets SQL command
            sql = "UPDATE Channel SET editor_id = %s WHERE ID = %s"
        # operations
        elif user_type == '2':
            # sets SQL command
            sql = "UPDATE Channel SET ops_id = %s WHERE ID = %s"
        # manager
        elif user_type == '1':
            # sets SQL command
            sql = "UPDATE Channel SET manager_id = %s WHERE ID = %s"
        # executes SQL command
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        # Logging
        log_data = {
            "action": "assign_user_to_channel",
            "author_id": author['user_id'],
            "data": {
                "user_id": user_id,
                "channel_id": channel_id,
                "user_type": user_type
            }
        }
        self.log_action(2, log_data)

    def assign_creator_to_channel(self, user_id, channel_id, author):
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result == None:
            return {
                "error": "Channel does not exist"
            }
        sql = "UPDATE Channel SET creator_id = %s WHERE ID = %s"
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        log_data = {
            "action": "assign_creator_to_channel",
            "author_id": author['user_id'],
            "data": {
                "user_id": user_id,
                "channel_id": channel_id
            }
        }
        self.log_action(2, log_data)

    def assign_editor_to_channel(self, user_id, channel_id, author):
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result == None:
            return {
                "error": "Channel does not exist"
            }
        sql = "UPDATE Channel SET editor_id = %s WHERE ID = %s"
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        log_data = {
            "action": "assign_editor_to_channel",
            "author_id": author['user_id'],
            "data": {
                "user_id": user_id,
                "channel_id": channel_id
            }
        }
        self.log_action(2, log_data)

    def assign_manager_to_channel(self, user_id, channel_id, author):
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result == None:
            return {
                "error": "Channel does not exist"
            }
        sql = "UPDATE Channel SET manager_id = %s WHERE ID = %s"
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        log_data = {
            "action": "assign_manager_to_channel",
            "author_id": author['user_id'],
            "data": {
                "user_id": user_id,
                "channel_id": channel_id
            }
        }
        self.log_action(2, log_data)

    def assign_ops_to_channel(self, user_id, channel_id, author):
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        if result == None:
            return {
                "error": "Channel does not exist"
            }
        sql = "UPDATE Channel SET ops_id = %s WHERE ID = %s"
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        log_data = {
            "action": "assign_ops_to_channel",
            "author_id": author['user_id'],
            "data": {
                "user_id": user_id,
                "channel_id": channel_id
            }
        }
        self.log_action(2, log_data)

    # function to login a user and return user details if successfull
    def login_user(self, user_email, password):
        # executes SQL command
        sql = "SELECT * FROM User WHERE email = %s"
        val = (user_email,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        # User not found
        if result == None:
            return {
                "success": False,
                "error": "User does not exist"
            }
        # User deleted
        elif result[5] == 1:
            return {
                "success": False,
                "error": "User is disabled or deleted please contact the Administrator"
            }
        # User found
        elif result[5] == 0: 
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

    ## TEST FUNCTIONS FOR DEBUGGING
    # Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
    def clearpro(self):
        self.cursor.execute("DROP DATABASE {}".format(self.dbname))
        self.dbconnect.commit()
        print("Database cleared")