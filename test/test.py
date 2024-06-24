import mysql.connector
import envfile
import bcrypt

vpass = input("Enter password: ")
vpass = vpass.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(vpass, salt)
print(hashed)
upass = input("Enter password again: ")
upass = upass.encode('utf-8')
if bcrypt.checkpw(upass, hashed):
    print("Match")