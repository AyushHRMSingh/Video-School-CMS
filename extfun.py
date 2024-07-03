import json
import bcrypt
import mysql.connector
import time

class VidSchool:
    # constructor function
    def __init__(self, dbhost, dbusername, dbpassword, dbname):
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
    
    def get_users_by_role(self, user_type, author):
        # checks permissions
        # executes SQL command
        sql = "SELECT * FROM User WHERE role = %s"
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
    def edit_user(self, user_name, user_id, user_email, password, user_type, author):
        # checks permissions
        if author['user_type'] == 0:
            # stores default values from DB
            defvalue = self.get_user(user_id)
            # sets values to default if None
            user_name = user_name if user_name != None else defvalue[1]
            user_email = user_email if user_email != None else defvalue[2]
            hashpass = self.hash_password(password) if password != None else defvalue[3]
            user_type = user_type if user_type != None else defvalue[4]
            # executes SQL command
            sql = "UPDATE User SET name = %s, email = %s, password = %s, role = %s WHERE ID = %s"
            val = (user_name, user_email, hashpass, user_type, user_id)
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
    def add_video(self, channel_id, video_name, creator_id, editor_id, manager_id, ops_id, author):
        # checks user is higher permissions than ops
        if author['user_type'] < 2:
            # executes SQL command
            sql = "INSERT INTO Video (name, channel_id, creator_id, editor_id, manager_id, ops_id, status) VALUES (%s, %s, %s, %s, %s, %s, 0)"
            val = (video_name, channel_id, creator_id, editor_id, manager_id, ops_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # Logging
            log_data = {
                "action": "add_video",
                "author_id": author['user_id'],
                "data": {
                    "video_name": video_name,
                    "creator_id": creator_id,
                    "editor_id": editor_id,
                    "manager_id": manager_id,
                    "ops_id": ops_id
                }
            }
            self.log_action(3, log_data)

    # function to update a video in the database
    def update_video(self, video_id, video_name, creator_id, editor_id, manager_id, ops_id, author):
        # stores values from DB as default
        defvalue = self.get_video(video_id)
        # if value is None, set to default value
        video_name = video_name if video_name != None else defvalue[1]
        creator_id = creator_id if creator_id != None else defvalue[2]
        editor_id = editor_id if editor_id != None else defvalue[3]
        manager_id = manager_id if manager_id != None else defvalue[4]
        ops_id = ops_id if ops_id != None else defvalue[5]
        # executes SQL command
        sql = "UPDATE Video SET name = %s, creator_id = %s, editor_id = %s, manager_id = %s, ops_id = %s WHERE ID = %s"
        val = (video_name, creator_id, editor_id, manager_id, ops_id, video_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        # Logging
        log_data = {
            "action": "update_video",
            "author_id": author['user_id'],
            "data": {
                "video_id": video_id,
                "video_name": video_name,
                "creator_id": creator_id,
                "editor_id": editor_id,
                "manager_id": manager_id,
            }
        }
        self.log_action(3, log_data)

    # function to set the status of a video
    def set_video_status(self, video_id, status, author, message = None):
        # checks if message is set
        if message != None:
            set_message = True
        # checks differen usertypes to check if action is permitted
        # creator
        if author['user_type'] == 4:
            if status == 1:
                # executes SQL command
                sql = "UPDATE Video SET status = 1 WHERE ID = %s"
                val = (video_id,)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                # storing log data in var
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status
                    }
                }
            else:
                return {
                    "error": "You do not have permission to set that status"
                }
        # editor
        elif author['user_type'] == 3:
            if status == 2 or status == 3:
                # executes SQL command
                sql = "UPDATE Video SET status = %s WHERE ID = %s"
                val = (status, video_id)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                # storing log data in var
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status
                    }
                }
            else:
                return {
                    "error": "You do not have permission to set that status"
                }
        # operations
        elif author['user_type'] == 2:
            if status == 2 or status == 4:
                sql = "UPDATE Video SET status = %s WHERE ID = %s"
                val = (status, video_id)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                # storing log data in var
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status
                    }
                }
            else:
                return {
                    "error": "You do not have permission to set that status"
                }
        # manager and admin
        elif author['user_type'] == 1 or author['user_type'] == 0:
            # executes SQL command
            sql = "UPDATE Video SET status = %s WHERE ID = %s"
            val = (status, video_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # storing log data in var
            log_data = {
                "action": "set_video_status",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id,
                    "status": status
                }
            }
        else:
            # return if invalid author
            return {
                "error": "INVALID AUTHOR"
            }
        # if message is set, add message to log data
        if set_message:
            log_data['data']['message'] = message
        self.log_action(3, log_data)
        
    # function to delete a video from the database
    def set_delete_video(self, video_id, author):
        # checks that user is higher than ops
        if author['user_type'] <2:
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

    # function to get all videos from the database
    def get_videos(self):
        # executes SQL command
        sql = "SELECT * FROM Video"
        self.cursor.execute(sql)
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
    # # TO BE REPLACED FOR GOOGLE INTEGRATION
    def add_channel(self, channel_name, url, platform, creator_id, editor_id, manager_id, ops_id, author):
        # checks if user is admin
        if author['user_type'] == 0:
            # executes SQL command
            sql = "INSERT INTO Channel (name, url ,platform, creator_id, editor_id, manager_id, ops_id, status) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"
            val = (channel_name, url, platform, creator_id, editor_id, manager_id, ops_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            # gets channel ID after adding
            sql = "SELECT ID FROM Channel WHERE name = %s AND url = %s AND platform = %s"
            val = (channel_name, url, platform)
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

    # function to edit a channel in the database
    def edit_channel(self, channel_id, channel_name, url, platform, creator_id, editor_id, manager_id, ops_id, status, author):
        # checks if user is admin
        if author['user_type'] == 0:
            # stores default values from DB
            defvalue = self.get_channel(channel_id)
            # sets values to default if None
            channel_name = channel_name if channel_name != None else defvalue[1]
            url = url if url != None else defvalue[2]
            platform = platform if platform != None else defvalue[3]
            creator_id = creator_id if creator_id != None else defvalue[4]
            editor_id = editor_id if editor_id != None else defvalue[5]
            manager_id = manager_id if manager_id != None else defvalue[6]
            ops_id = ops_id if ops_id != None else defvalue[7]
            status = status if status != None else defvalue[8]
            # executes SQL command
            sql = "UPDATE Channel SET name = %s, url=%s, platform = %s, creator_id = %s, editor_id = %s, manager_id = %s, ops_id = %s, status = %s WHERE ID = %s"
            val = (channel_name, url, platform, creator_id, editor_id, manager_id, ops_id, status, channel_id)
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
        elif result[4] == 1:
            return {
                "success": False,
                "error": "User is disabled or deleted please contact the Administrator"
            }
        # User found
        elif result[4] == 0: 
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
                    "user_type": result[4],
                    "user_email": result[2]
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
        sql = "INSERT INTO LogTable (log_type, log_date,log_data) VALUES (%s, %s, %s)"
        val = (log_type, log_time, log_data)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    # get all logs
    def get_logs(self):
        # executes SQL command
        sql = "SELECT * FROM LogTable"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    ## TEST FUNCTIONS FOR DEBUGGING
    # Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
    def clearpro(self):
        self.cursor.execute("DROP DATABASE {}".format(self.dbname))
        self.dbconnect.commit()
        print("Database cleared")