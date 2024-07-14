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
2. Go to the project directory
```bash
path/to/project/Video-School-CMS
```
3. Create a virtual environment
```bash
python -m venv venv
```
4. Activate the virtual environment
```
source /path/to/venv/bin/activate # Linux and Mac Systems
venv\Scripts\activate.bat # Windows systems
```
5. Install the required packages
```bash
pip install -r Source/requirements.txt
```
6. Create a YAML file in the root directory of the project and name it 'env.yml'. Add the following lines to the file
```yaml
dbvar:
  host : 'localhost'
  dbuser : 'root'
  dbpass : '<replace with the password for MySQL>'
  dbname : 'VIDEOSCHOOL'
```
7. Setup the MySQL database for the project by running the following file
```bash
python Setup/reset_db.py
```
9. Setup the Apache Web Server to reverse proxy the Flask application. Edit the specified configuration file and edit or add the following lines
    - Uncomment or add the following lines
    ```apache
    Include /private/etc/apache2/extra/httpd-vhosts.conf
    LoadModule proxy_module libexec/apache2/mod_proxy.so
    LoadModule proxy_http_module libexec/apache2/mod_proxy_http.so
    ```
    - Add the following lines to the httpd-vhosts.conf file and also comment out the example virtual hosts
    ```apache
    <VirtualHost *:80>
        ProxyPreserveHost On
        ProxyRequests Off
        ProxyPass / http://127.0.0.1:8089/
        ProxyPassReverse / http://127.0.0.1:8089/
    </VirtualHost>
    ```
10. Start or restart the Apache Web Server after editing the above files
11. Create a project in Google Console and enable the Youtube Analytics API v2 and Youtube Data API v3
12. From the project dashboard click on OAuth consent screen to set it up (remember to add your gmail account to the list of Test User when in the testing phase)
13. After finishing the setup of th OAuth consent screen go to the Credentials tab, select the "CREATE CREDENTIALS" and then select "OAuth client ID" option
14. Select "Web application" as the Application type, enter the other relevant details
    * for local testing remember to add "http://localhost/oauth2callback" as the authorized redirect URI
15. Once the OAuth 2.0 CLient ID is created download the client secret json file
16. Place the json file in the root of the folder rename it to "client_secrets.json"
11. Run the Flask application
```bash
python /Path/to/Video-School-CMS/Source/wsgi.py
```