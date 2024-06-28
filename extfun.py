import json
import bcrypt
import mysql.connector
import time

class VidSchool:
    def __init__(self, dbhost, dbusername, dbpassword, dbname):
        self.dbconnect = mysql.connector.connect(
            host = dbhost,
            user = dbusername,
            password = dbpassword
        )
        self.cursor = self.dbconnect.cursor()
        self.dbname = dbname
        self.sqlcommands = [
            # create database if not exists
            "CREATE DATABASE IF NOT EXISTS {}".format(self.dbname),
            # user the database
            "USE  {}".format(self.dbname),
            # create user table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS User (ID INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, role TINYINT NOT NULL DEFAULT 0, status TINYINT NOT NULL DEFAULT 0)",
            # add default admin user
            # f"INSERT IGNORE INTO User (email, password, role, status) VALUES ('root@root.com', '{self.hash_password('root')}', 0, 0)",
            # create channel table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS Channel (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, platform TINYINT NOT NULL DEFAULT 0, creator_id INT, editor_id INT, manager_id INT, operator_id INT, status TINYINT NOT NULL DEFAULT 0, tokens JSON NOT NULL DEFAULT ('{}'))",
            # create video table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS Video (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, channel_id INT NOT NULL, url VARCHAR(255) UNIQUE, creator_id INT, editor_id INT, manager_id INT, upload_date INT, status TINYINT NOT NULL DEFAULT 0)",
            # create log_table table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS LogTable (ID INT AUTO_INCREMENT PRIMARY KEY, log_type TINYINT NOT NULL DEFAULT 0, log_date INT NOT NULL, log_data JSON NOT NULL DEFAULT ('{}'))",

        ]
        print("Connected to database")
    
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
    def add_user(self, user_email, password, user_type, author):
        if author['user_type'] == 0:
            hashpass = self.hash_password(password)
            sql = "INSERT INTO User (email, password, role, status) VALUES (%s, %s, %s, 0)"
            val = (user_email, hashpass, user_type)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            self.cursor.execute("SELECT ID FROM User WHERE email = %s AND password = %s", (user_email, hashpass))
            user = self.cursor.fetchone()
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

    def delete_user(self, user_id, author):
        if author['user_type'] == 0:
            sql = "UPDATE User SET status = 1 WHERE ID = %s"
            val = (user_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        if author['user_type'] == 0:
            sql = "SELECT * FROM User"
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result
        else:
            return {
                "error": "You do not have permission to view this data"
            }
    
    # function to get a specific user from the database
    def get_user(self, user_id):
        sql = "SELECT * FROM User WHERE ID = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result
    
    def edit_user(self, user_id, user_email, password, user_type, author):
        if author['user_type'] == 0:
            defvalue = self.get_user(user_id)
            user_email = user_email if user_email != None else defvalue[1]
            hashpass = self.hash_password(password) if password != None else defvalue[2]
            user_type = user_type if user_type != None else defvalue[3]
            sql = "UPDATE User SET email = %s, password = %s, role = %s WHERE ID = %s"
            val = (user_email, hashpass, user_type, user_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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

    ### VIDEO FUNCTIONS
    # function to add a video to the database
    def add_video(self, video_name, creator_id, editor_id, manager_id, author):
        if author['user_type'] < 3:
            sql = "INSERT INTO Video (name, creator_id, editor_id, manager_id, status) VALUES (%s, %s, %s, %s, 0)"
            val = (video_name, creator_id, editor_id, manager_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action": "add_video",
                "author_id": author['user_id'],
                "data": {
                    "video_name": video_name,
                    "creator_id": creator_id,
                    "editor_id": editor_id,
                    "manager_id": manager_id,
                }
            }
            self.log_action(3, log_data)

    # function to update a video in the database
    def update_video(self, video_id, video_name, creator_id, editor_id, manager_id, author):
        if author['user_type'] < 3:
            defvalue = self.get_video(video_id)
            video_name = video_name if video_name != None else defvalue[1]
            creator_id = creator_id if creator_id != None else defvalue[2]
            editor_id = editor_id if editor_id != None else defvalue[3]
            manager_id = manager_id if manager_id != None else defvalue[4]
            sql = "UPDATE Video SET name = %s, creator_id = %s, editor_id = %s, manager_id = %s WHERE ID = %s"
            val = (video_name, creator_id, editor_id, manager_id, video_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        if status == 0:
            sql = "UPDATE Video SET status = 0 WHERE ID = %s"
            val = (video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action": "set_video_status",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id,
                    "status": status,
                    "message": message if message != None else "No message"
                }
            }
            self.log_action(3, log_data)
        elif status == 1:
            sql = "UPDATE Video SET status = 1 WHERE ID = %s"
            val = (video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action": "set_video_status",
                "author_id": author['user_id'],
                "data": {
                    "video_id": video_id,
                    "status": status,
                    "message": message if message != None else "No message"
                }
            }
            self.log_action(3, log_data)
        elif status == 2 or status == 3:
            if author['user_type'] <= 3:
                sql = "UPDATE Video SET status = 2 WHERE ID = %s"
                val = (video_id,)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status,
                        "message": message if message != None else "No message"
                    }
                }
                self.log_action(3, log_data)
        elif status == 4:
            if author['user_type'] <=2 or author['user_type'] == 4:
                sql = "UPDATE Video SET status = 4 WHERE ID = %s"
                val = (video_id,)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status,
                        "message": message if message != None else "No message"
                    }
                }
                self.log_action(3, log_data)
        elif status == 6:
            if author['user_type'] <= 2:
                sql = "UPDATE Video SET status = 6 WHERE ID = %s"
                val = (video_id,)
                self.cursor.execute(sql, val)
                self.dbconnect.commit()
                log_data = {
                    "action": "set_video_status",
                    "author_id": author['user_id'],
                    "data": {
                        "video_id": video_id,
                        "status": status,
                        "message": message if message != None else "No message"
                    }
                }
                self.log_action(3, log_data)
        else:
            return {
                "error": "Invalid status"
            }

    # function to delete a video from the database
    def set_delete_video(self, video_id, author):
        if author['user_type'] >2:
            sql = "UPDATE Video SET status = 7 WHERE ID = %s"
            val = (video_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        sql = "SELECT * FROM Video"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    # function to get a specific video from the database
    def get_video(self, video_id):
        sql = "SELECT * FROM Video WHERE ID = %s"
        val = (video_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result

    ### CHANNEL FUNCTIONS
    # # TO BE REPLACED FOR GOOGLE INTEGRATION
    def add_channel(self,channel_id, channel_name, platform, author):
        if author['user_type'] == 0:
            sql = "INSERT INTO Channel (ID, name, platform, status) VALUES (%s, %s, %s, 1)"
            val = (channel_id, channel_name, platform)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        if author['user_type'] == 0:
            sql = "UPDATE Channel SET status = 3 WHERE ID = %s"
            val = (channel_id,)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action": "delete_channel",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id
                }
            }
            self.log_action(2, log_data)

    def edit_channel(self, channel_id, channel_name, platform, author):
        if author['user_type'] == 0:
            defvalue = self.get_channel(channel_id)
            channel_name = channel_name if channel_name != None else defvalue[1]
            platform = platform if platform != None else defvalue[2]
            sql = "UPDATE Channel SET name = %s, platform = %s WHERE ID = %s"
            val = (channel_name, platform, channel_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
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
        if author['user_type'] == 0:
            sql = "UPDATE Channel SET status = %s WHERE ID = %s"
            val = (status, channel_id)
            self.cursor.execute(sql, val)
            self.dbconnect.commit()
            log_data = {
                "action": "update_channel_status",
                "author_id": author['user_id'],
                "data": {
                    "channel_id": channel_id,
                    "status": status
                }
            }
            self.log_action(2, log_data)
    
    def get_channels(self):
        sql = "SELECT * FROM Channel;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
        
    def get_channel(self, channel_id):
        sql = "SELECT * FROM Channel WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        return result

    # function to add a user to a channel with a specific role
    def assign_user_to_channel(self, user_id, channel_id, user_type, author):
        if user_type == '4':
            sql = "UPDATE Channel SET creator_id = %s WHERE ID = %s"
        elif user_type == '3':
            sql = "UPDATE Channel SET editor_id = %s WHERE ID = %s"
        elif user_type == '2':
            sql = "UPDATE Channel SET operator_id = %s WHERE ID = %s"
        elif user_type == '1':
            sql = "UPDATE Channel SET manager_id = %s WHERE ID = %s"
        val = (user_id, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
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

    # function to login a user and return user details if successfull
    def login_user(self, user_email, password):
        sql = "SELECT * FROM User WHERE email = %s"
        val = (user_email,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchone()
        # No user found
        if result == None:
            return {
                "success": False,
                "error": "User does not exist"
            }
        # User deleted
        elif result[4] == '0':
            return {
                "success": False,
                "error": "User is disabled or deleted please contact the Administrator"
            }
        # User found and password matches
        elif bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            log_data = {
                "action": "login",
                "data": {
                    "user_id": result[0],
                    "user_email": user_email,
                    "login_time": int( time.time() )
                }
            }
            self.log_action(0, log_data)
            return {
                "success": True,
                "user_id": result[0],
                "user_type": result[3],
                "user_email": result[1]
            }
        
    # log every action
    def log_action(self, log_type, log_data, log_time = int( time.time() )):
        log_data = json.dumps(log_data)
        print(log_data)
        print(type(log_data))
        sql = "INSERT INTO LogTable (log_type, log_date,log_data) VALUES (%s, %s, %s)"
        val = (log_type, log_time, log_data)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    def get_logs(self):
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
