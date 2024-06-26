import bcrypt
import mysql.connector

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
            # create channel table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS Channel (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, platform TINYINT NOT NULL DEFAULT 0, creator_id INT, editor_id INT, manager_id INT, operator_id INT, status TINYINT NOT NULL DEFAULT 0, tokens JSON NOT NULL DEFAULT ('{}'))",
            # create video table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS Video (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, url VARCHAR(255) UNIQUE, creator_id INT NOT NULL, editor_id INT NOT NULL, manager_id INT NOT NULL, upload_date INT NOT NULL, status TINYINT NOT NULL DEFAULT 0)",
            # create login log table if it doesn't exists
            "CREATE TABLE IF NOT EXISTS LoginLog (ID INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, log_type TINYINT NOT NULL DEFAULT 0, log_date INT NOT NULL)",
        ]
        print("Connected to database")
    
    def __del__(self):
        self.dbconnect.close()
        print("Disconnected from database")

    # MAJOR TODO
    # UPDATE ALL ROLE RELATED COMMANDS

    # hashing and salting password for security with bcrypt library
    def hash_password(password):
        password = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')

    # sqlcommands to create the database and table during setup

    # Setup the database with the proper schema
    def setupdb(self):
        for command in self.sqlcommands:
            self.cursor.execute(command)
            self.dbconnect.commit()
        print("Setup complete")

    # function to add a user to the database ONLY FOR ADMIN
    def add_user(self, user_email, password, user_type):
        hashpass = self.hash_password(password)
        sql = "INSERT INTO User (user_email, password, user_type, status) VALUES (%s, %s, %s, 1)"
        val = (user_email, hashpass, user_type)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    def delete_user(self, user_id):
        sql = "UPDATE User SET status = 0 WHERE ID = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    # function to add a channel to the database ONLY FOR ADMIN?
    # # TO BE REPLACED FOR GOOGLE INTEGRATION
    def add_channel(self,channel_id, channel_name, platform):
        sql = "INSERT INTO Channel (ID, name, platform, status) VALUES (%s, %s, %s, 1)"
        val = (channel_id, channel_name, platform)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    def delete_channel(self, channel_id):
        sql = "UPDATE Channel SET status = 'DELETED' WHERE ID = %s"
        val = (channel_id,)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    def update_channel_status(self, channel_id, status):
        sql = "UPDATE Channel SET status = %s WHERE ID = %s"
        val = (status, channel_id)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()
        
    # function to add a user to a channel with a specific role
    def assign_user_to_channel(self, user_id, channel_id, user_type):
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

    # function to track when users log in and out of the system
    def login_log(self, user_id, log_type, log_date):
        sql = "INSERT INTO LoginLog (user_id, log_type, log_date) VALUES (%s, %s, %s)"
        val = (user_id, log_type, log_date)
        self.cursor.execute(sql, val)
        self.dbconnect.commit()

    # function to login a user and return user details if successfull
    def login_user(self, user_email, password):
        sql = "SELECT * FROM User WHERE user_email = %s"
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
            return {
                "success": True,
                "user_id": result[0],
                "user_type": result[3],
                "user_email": result[1]
            }


    ## TEST FUNCTIONS FOR DEBUGGING
    # Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
    def cleardb(self):
        self.cursor.execute("DROP TABLE TUser")
        self.dbconnect.commit()
        print("Database cleared")

    # Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
    def clearpro(self):
        self.cursor.execute("DROP DATABASE {}".format(self.dbname))
        self.dbconnect.commit()
        print("Database cleared")

    def showuser(self, user_id, passa):
        sql = "SELECT * FROM User WHERE ID = %s"
        val = (user_id,)
        self.cursor.execute(sql, val)
        result = self.cursor.fetchall()
        print(result)