import bcrypt
import mysql.connector
import envfile

# hashing and salting password for security with bcrypt library
def hash_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

# function to return database connection to server for code reusability
def connectdb():
    dbconnect = mysql.connector.connect(
        host="localhost",
        user="root",
        password=envfile.dbpass,
    )
    cursor = dbconnect.cursor()
    return dbconnect, cursor

# sqlcommands to create the database and table during setup
sqlcommands = [
    # create database if not exists
    "CREATE DATABASE IF NOT EXISTS {}".format(envfile.dbname),
    # user the database
    "USE  {}".format(envfile.dbname),
    # create user table if it doesn't exists
    "CREATE TABLE IF NOT EXISTS User (ID INT AUTO_INCREMENT PRIMARY KEY, user_email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, user_type ENUM('USER_ADMIN', 'USER_CREATOR', 'USER_EDITOR', 'USER_MANAGER','USER_OPS') NOT NULL, status ENUM('ACTIVE', 'INACTIVE') NOT NULL)",
    # create channel table if it doesn't exists
    "CREATE TABLE IF NOT EXISTS Channel (ID VARCHAR(255) PRIMARY KEY, channel_name VARCHAR(255) UNIQUE NOT NULL, platform ENUM('YOUTUBE', 'FACEBOOK', 'INSTAGRAM') NOT NULL, user_creator INT, user_editor INT, user_manager INT, status ENUM('ACTIVE', 'INACTIVE', 'TO_BE_DELETED', 'DELETED') NOT NULL, tokens JSON NOT NULL)",
    # create video table if it doesn't exists
    "CREATE TABLE IF NOT EXISTS Video (ID INT AUTO_INCREMENT PRIMARY KEY, video_name VARCHAR(255) UNIQUE NOT NULL, url VARCHAR(255) UNIQUE, channel_id VARCHAR(255) NOT NULL, creator_id INT NOT NULL, editor_id INT NOT NULL, manager_id INT NOT NULL, upload_date INT NOT NULL, status ENUM('VIDEO_STATUS_TO_BE_CREATED', 'VIDEO_STATUS_SHOT', 'VIDEO_STATUS_EDITED', 'VIDEO_STATUS_TO_BE_RESHOT', 'VIDEO_STATUS_TO_BE_REDITED', 'VIDEO_STATUS_APPROVED', 'VIDEO_STATUS_UPLOADED', 'VIDEO_STATUS_DELETED') NOT NULL)",
    # create login log table if it doesn't exists
    "CREATE TABLE IF NOT EXISTS LoginLog (ID INT AUTO_INCREMENT PRIMARY KEY, user_id INT NOT NULL, log_type ENUM('LOGIN', 'LOGOUT') NOT NULL, log_date INT NOT NULL)",
]

# Setup the database with the proper schema
def setupdb():
    dbconnect,cursor = connectdb()
    for command in sqlcommands:
        cursor.execute(command)
        dbconnect.commit()
    print("Setup complete")

# function to add a user to the database ONLY FOR ADMIN
def add_user(user_email, password, user_type):
    hashpass = hash_password(password)
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "INSERT INTO User (user_email, password, user_type, status) VALUES (%s, %s, %s, 'ACTIVE')"
    val = (user_email, hashpass, user_type)
    cursor.execute(sql, val)
    dbconnect.commit()

def delete_user(user_id):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "UPDATE User SET status = 'INACTIVE' WHERE ID = %s"
    val = (user_id,)
    cursor.execute(sql, val)
    dbconnect.commit()

# function to add a channel to the database ONLY FOR ADMIN?
# # TO BE REPLACED FOR GOOGLE INTEGRATION
def add_channel(channel_id, channel_name, platform):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "INSERT INTO Channel (ID, channel_name, platform, status) VALUES (%s, %s, %s, 'ACTIVE')"
    val = (channel_id, channel_name, platform)
    cursor.execute(sql, val)
    dbconnect.commit()

def delete_channel(channel_id):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "UPDATE Channel SET status = 'DELETED' WHERE ID = %s"
    val = (channel_id,)
    cursor.execute(sql, val)
    dbconnect.commit()

def update_channel_status(channel_id, status):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "UPDATE Channel SET status = %s WHERE ID = %s"
    val = (status, channel_id)
    cursor.execute(sql, val)
    dbconnect.commit()
    
# function to add a user to a channel with a specific role
def assign_user_to_channel(user_id, channel_id, user_type):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    if user_type == 'USER_CREATOR':
        sql = "UPDATE Channel SET user_creator = %s WHERE ID = %s"
    elif user_type == 'USER_EDITOR':
        sql = "UPDATE Channel SET user_editor = %s WHERE ID = %s"
    elif user_type == 'USER_MANAGER':
        sql = "UPDATE Channel SET user_manager = %s WHERE ID = %s"
    val = (user_id, channel_id)
    cursor.execute(sql, val)
    dbconnect.commit()

def login_log(user_id, log_type, log_date):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "INSERT INTO LoginLog (user_id, log_type, log_date) VALUES (%s, %s, %s)"
    val = (user_id, log_type, log_date)
    cursor.execute(sql, val)
    dbconnect.commit()



## TEST FUNCTIONS FOR DEBUGGING

# Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
def cleardb():
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    cursor.execute("DROP TABLE TUser")
    dbconnect.commit()
    print("Database cleared")

# Clear the database, ONLY FOR TESTING AND DEBUGGING PURPOSES
def clearpro():
    dbconnect,cursor = connectdb()
    cursor.execute("DROP DATABASE {}".format(envfile.dbname))
    dbconnect.commit()
    print("Database cleared")

def showuser(user_id):
    dbconnect,cursor = connectdb()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "SELECT * FROM User WHERE ID = %s"
    val = (user_id,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    print(result)

