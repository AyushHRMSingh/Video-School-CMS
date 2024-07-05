# VideoSchool Content Management System
<br>
This is a content management system for a video school. It allows the company to manage employees, videos and channels. The system is build using Python Flask, MySQL, and Apache Web Server.

## Features
- User authentication
- User roles
- User permissions
- Video CRUD
- Channel CRUD
- Employee CRUD
- Action logging

## Pre-requisites
1. Python 3.10.14
2. MySQL 8.4.0 LTS
3. Apache Web Server 2.4.60


## Installation
1. Clone the repository
2. Make sure you install all the specific version of the software as mentioned aboved in the prerequisites
- MacOS users can use Homebrew to install python3.10 with the command `brew install python@3.10`.
- Linux users can compile and make the packages themselves (remember when making the packages to setup openssl or else pip installs wont work).
3. Enter the project's Source directory
```bash
cd /path/to/Video-School-CMS/Source
```
4. Create a virtual environment
```bash
python3.10 -m venv vscms
```
5. Activate the virtual environment
```bash
source /path/to/Video-School-CMS/Source/vscms/bin/activate
```
6. Install the required packages
```bash
pip install -r requirements.txt --no-cache
```
    (note: MacOS users need to run `xcode-select --install` before running the above command to install the required packages)
7. Create an env.py file in both the Source and Setup directories with the following content
```python
host = 'localhost'
dbuser = 'root'
dbpass = '<MySQL password>'
dbname = 'VIDEOSCHOOL'
```
    note: Replace <MySQL password> with your MySQL password and feel free to customize all aspects if you're modifiying the database schema or program
8. To setup the database before use, run the sqlsetup.py file
```bash
python path/to/Video-School-CMS/Setup/sqlsetup.py
```
9. To setup the server first run
```bash
mod_wsgi-express setup-server wsgi.py --port=80 --user=daemon --group=daemon --server-root=/path/to/Video-School-CMS/Server
```
10. To then start the server for good run
```bash
sudo /path/to/Video-School-CMS/Server/apachectl start
```
11. The server is now running, to visit it navigate to http://localhost, you can log into the portal with a default admin account with the following credentials:
```bash
username: root@root.com
password: root
```
    (note: This account is only for testing purposes, it is recommended to create a new admin account and delete this one)
12. To stop the server run
```bash
sudo /path/to/Video-School-CMS/Server/apachectl stop
```


Functionalities pending :
- Customized views for all roles lower than Admin i.e. manager, ops, editor and creator
- Google OAuth and Youtube Analytics integration (Phase 2)
- Built in AI content generation system (Phase 3)

## TroubleShooting
1. if getting the error that port 80 is already taken run the command `sudo lsof -i :80` in the CLI to find the process id and then run `sudo kill <process id (PID)>` to kill the process and then rerun the server start command

2. if you're getting the error about the server not being able to find modules while looking in the wrong environment reinstall mod_wsgi with the --no-cache option to ensure that the correct environment is being used

3. if in the error logs that the server is unable to find app.py or wsgi.py make sure you run the server setup command from within the Source directory