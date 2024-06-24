import bcrypt
import mysql.connector
import envfile

def hash_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

def add_user(email, password):
    hashed = hash_password(password)
    sql = "INSERT INTO TUser (email, password) VALUES (%s, %s)"
    val = (email, hashed)
    dbconnect = mysql.connector.connect(
        host="localhost",
        user="root",
        password=envfile.dbpass,
    )
    cursor = dbconnect.cursor()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    cursor.execute(sql, val)
    dbconnect.commit()
    print("User added")

def login(email, password):
    dbconnect = mysql.connector.connect(
        host="localhost",
        user="root",
        password=envfile.dbpass,
    )
    cursor = dbconnect.cursor()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    sql = "SELECT password FROM TUser WHERE email = %s"
    val = (email,)
    cursor.execute(sql, val)
    result = cursor.fetchone()
    if (result == None):
        print("User not found")
        return False
    if (bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8'))):
        print("Login success")
        return True
    else:
        print("Login failed")
        return False

def setup():
    dbconnect = mysql.connector.connect(
        host="localhost",
        user="root",
        password=envfile.dbpass,
    )
    cursor = dbconnect.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(envfile.dbname))
    cursor.execute("USE  {}".format(envfile.dbname))
    # email should be unique and add primary key ID
    cursor.execute("CREATE TABLE IF NOT EXISTS TUser (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255) UNIQUE, password VARCHAR(255))")
    dbconnect.commit()
    print("Setup complete")

def cleardb():
    dbconnect = mysql.connector.connect(
        host="localhost",
        user="root",
        password=envfile.dbpass,
    )
    cursor = dbconnect.cursor()
    try:
        cursor.execute("USE  {}".format(envfile.dbname))
    except:
        dbconnect.database = envfile.dbname
    cursor.execute("DROP TABLE TUser")
    dbconnect.commit()
    print("Database cleared")