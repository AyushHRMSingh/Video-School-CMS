import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import csv
import datetime
from type_vars import *
from video_enumeration import vidstatus


PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
Upload_Folder = os.path.join(PROJECT_PATH+'/Data')
ALLOWED_EXTENSIONS = ['csv','txt']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Upload_Folder
app.secret_key = 'xt2505'

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No file provided")
            return redirect(request.url)
        if file and file.filename.split('.')[1] in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            csv_list = handle_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            csv_list = check_n_format_csv(csv_list)
            if type(csv_list) == str:
                return "error"
            return render_template('view_csv.html', csv_list=csv_list, video_status=vidstatus)
        else:
            return "Invalid file"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method='post' enctype='multipart/form-data'>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def handle_csv(url):
    sqllist=[]
    # opens the csv file and reads it
    with open(url, "r") as csvfile:
        rows = csv.reader(csvfile, dialect="excel")
        rows = list(rows)
        for i in range(0, len(rows)):
            # skip row if name or id are empty
            if rows[i][0] == "":
                continue
            if rows[i][1] == "":
                continue
            sqllist.append(rows[i])
    # returs csv file as a list with no empty rows
    return sqllist

# Check the csv formatting and validity of entries such as time and status
def check_n_format_csv(csv_list):
    # check the top row for formatting
    head = csv_list[0]
    if head[0][1:] != 'id' or head[1] != 'title' or head[2] != 'url' or head[3] != 'shoot_timestamp' or head[4] != 'edit_timestamp' or head[5] != "upload_timestamp" or head[6] != 'comment':
        print(head[0][1:] != 'id', head[1] != 'title', head[2] != 'url', head[3] != 'shoot_timestamp', head[4] != 'edit_timestamp', head[5] != "upload_timestamp", head[6] != 'comment')
        return "FIX TABLE HEADERS"
    
    resulting_csv_list = []
    # checking all data entries and append the valid ones
    for i in range(1, len(csv_list)):
        row = csv_list[i]
        if type(row[0]) != str:
            return "ID column at row "+str(i)+" is not an str"
        else:
            if row[0].isdigit() == False:
                return "invalid id entry at row "+str(i)
        if row[3] != "":
            try:
                row[3] = int(datetime.datetime.strptime(row[3], '%d-%b-%y').timestamp())
                if row[4] != "":
                    try:
                        row[4] = int(datetime.datetime.strptime(row[4], '%d-%b-%y').timestamp())
                        if row[5] != "":
                            try:
                                row[5] = int(datetime.datetime.strptime(row[5], '%d-%b-%y').timestamp())
                            except:
                                return "error on row "+row[0]+" at shoot timestamp "+row[5]
                    except:
                        return "error on row "+row[0]+" at shoot timestamp "+row[4]
            except:
                return "error on row "+row[0]+" at shoot timestamp "+row[3]
        if row[3] != "" and row[4] != "" and row[5] != "" :
            row.append(VIDEO_STATUS_UPLOADED)
        elif row[3] != "" and row[4] != "" and row[5] == "":
            row.append(VIDEO_STATUS_EDITED)
        elif row[3] != "" and row[4] == "" and row[5] == "":
            row.append(VIDEO_STATUS_SHOT)
        elif row[3] == "" and row[4] == "" and row[5] == "":
            row.append(VIDEO_STATUS_TO_BE_CREATED)
        resulting_csv_list.append(row)
    return resulting_csv_list


# Main entry point of the application
if __name__ == '__main__':
    app.run(debug=True, port=8089,host='localhost')

# \ufeff