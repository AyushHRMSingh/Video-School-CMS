import bcrypt
import extfun

def login():
    print("login")
    email = input("Email: ")
    password = input("Password: ")
    extfun.login(email, password)

def register():
    print("register")
    email = input("Email: ")
    password = input("Password: ")
    extfun.add_user(email, password)

def main():
    extfun.setup()
    opt = input("1. Login\n2. Register\n")
    if (opt == "1"):
        login()
    elif (opt == "2"):
        register()
    else:
        print("Invalid option")

# def main():
#     spass = input("Enter password: ")
#     spass = spass.encode('utf-8')
#     salt = bcrypt.gensalt()
#     hashed = bcrypt.hashpw(spass, salt)
#     print(hashed)
#     hashed = hashed.decode('utf-8')
#     print(hashed)
#     spass = input("Enter password again: ")
#     spass = spass.encode('utf-8')
#     hpass = input("enter the hash: ")
#     hpass = hpass.encode('utf-8')
#     if (bcrypt.checkpw(spass, hpass)):
#         print("Login success")
#     else:
#         print("Login failed")

if __name__ == "__main__":
    main()