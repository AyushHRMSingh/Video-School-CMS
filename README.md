# VideoSchool Content Management System

## Description
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
2. Create a virtual environment using conda
```bash
conda create -n vscms python=3.10.14
```
3. Activate the virtual environment
```bash
conda activate vscms
```
4. Enter the project directory
```bash
cd /path/to/Video-School-CMS
```
5. Install the required packages
```bash
pip install -r requirements.txt --no-cache
```
6. To setup the database before use, run the sqlsetup.py file
```bash
python Setup/sqlsetup.py
```
7. To setup the server first run
```bash
mod_wsgi-express setup-server wsgi.py --port=80 --user=daemon --group=daemon --server-root=/path/to/Video-School-CMS/Server
```
8. To then start the server for good run
```bash
sudo /path/to/Video-School-CMS/Server/apachectl start
```
9. The server is now running, to visit it navigate to http://localhost, you can log into the portal with a default admin account with the following credentials:
```bash
username: root@root.com
password: root
```
(note: This account is only for testing purposes, it is recommended to create a new admin account and delete this one)
10. To stop the server run
```bash
sudo /path/to/Video-School-CMS/Server/apachectl stop
```


Functionalities pending :
- Customized views for all roles lower than Admin i.e. manager, ops, editor and creator
- Google OAuth and Youtube Analytics integration (Phase 2)
- Built in AI content generation system (Phase 3)