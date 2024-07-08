import mysql.connector
import bcrypt
import envfile
host = envfile.host
username = envfile.dbuser
password = envfile.dbpass
dbname = envfile.dbname

def hash_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

sqlcommands = [
    "DROP DATABASE IF EXISTS {}".format(dbname),
    # create database if not exists
    "CREATE DATABASE {}".format(dbname),
    # user the database
    "USE  {}".format(dbname),
    # create user table if it doesn't exists
    "CREATE TABLE User (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL,email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, role TINYINT NOT NULL DEFAULT 0, status TINYINT NOT NULL DEFAULT 0)",
    # add default admin user
    f"INSERT INTO User (name, email, password, role, status) VALUES ('root user','root@root.com', '{hash_password('root')}', 0, 0)",
    # create channel table if it doesn't exists
    "CREATE TABLE Channel (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, url VARCHAR(255), platform TINYINT NOT NULL DEFAULT 0, creator_id INT, editor_id INT, manager_id INT, ops_id INT, status TINYINT NOT NULL DEFAULT 0, tokens JSON NOT NULL DEFAULT ('{}'))",
    # create video table if it doesn't exists
    "CREATE TABLE Video (id INT AUTO_INCREMENT PRIMARY KEY, old_id VARCHAR(6) UNIQUE, title VARCHAR(255) UNIQUE NOT NULL, channel_id INT NOT NULL, shoot_timestamp INT, edit_timestamp INT, upload_timestamp INT, status TINYINT NOT NULL DEFAULT 0, comment LONGTEXT DEFAULT NULL)",
    # create log_table table if it doesn't exists
    "CREATE TABLE Log_Table (id INT AUTO_INCREMENT PRIMARY KEY, type TINYINT NOT NULL DEFAULT 0, date INT NOT NULL, data JSON NOT NULL DEFAULT ('{}'))",
]

def mainB():
    dbconnect = mysql.connector.connect(
        host=host,
        user=username,
        password=password
    )
    cursor = dbconnect.cursor()
    for command in sqlcommands:
        print("Executing command: ", command)
        cursor.execute(command)

mainB()