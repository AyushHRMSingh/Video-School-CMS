import mysql.connector
import sqlsetup
import envfile

host = envfile.host
username = envfile.dbuser
password = envfile.dbpass
dbname = envfile.dbname

dbconnect = mysql.connector.connect(
    host=host,
    user=username,
    password=password
)
cursor = dbconnect.cursor()
cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
cursor.close()
dbconnect.close()
print("Database deleted")
sqlsetup.mainB()