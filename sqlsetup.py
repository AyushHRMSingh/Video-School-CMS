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
    # create database if not exists
    "CREATE DATABASE {}".format(dbname),
    # user the database
    "USE  {}".format(dbname),
    # create user table if it doesn't exists
    "CREATE TABLE User (ID INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, role TINYINT NOT NULL DEFAULT 0, status TINYINT NOT NULL DEFAULT 0)",
    # add default admin user
    f"INSERT INTO User (email, password, role, status) VALUES ('root@root.com', '{hash_password('root')}', 0, 0)",
    # create channel table if it doesn't exists
    "CREATE TABLE Channel (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, platform TINYINT NOT NULL DEFAULT 0, creator_id INT, editor_id INT, manager_id INT, operator_id INT, status TINYINT NOT NULL DEFAULT 0, tokens JSON NOT NULL DEFAULT ('{}'))",
    # create video table if it doesn't exists
    "CREATE TABLE Video (ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, channel_id INT NOT NULL, url VARCHAR(255) UNIQUE, creator_id INT, editor_id INT, manager_id INT, operator_id INT, upload_date INT, status TINYINT NOT NULL DEFAULT 0)",
    # create log_table table if it doesn't exists
    "CREATE TABLE LogTable (ID INT AUTO_INCREMENT PRIMARY KEY, log_type TINYINT NOT NULL DEFAULT 0, log_date INT NOT NULL, log_data JSON NOT NULL DEFAULT ('{}'))",
]

def main():
    dbconnect = mysql.connector.connect(
        host=host,
        user=username,
        password=password
    )
    cursor = dbconnect.cursor()
    for command in sqlcommands:
        print("Executing command: ", command)
        cursor.execute(command)

main()