import time
import flask
import csv
from extfun import VidSchool
import datetime
import calendar

# FORMAT FOR CSV: [id, title, url, shoot_timestamp, edit_timestamp, upload_timestamp, comment]

# set of drop in functions for flask

# READING AND RETURNING THE UPLOADED CSV FILE
def handlecsv(url):
    sqllist=[]
    with open(url, "r") as csvfile:
        rows = csv.reader(csvfile, dialect="excel")
        rows = list(rows)
        # sqllist[0][0] = sqllist[0][0][:len(sqllist[0][0])-6]
        for i in range(0, len(rows)):
            if rows[i][0] == "":
                continue
            if rows[i][1] == "":
                continue
            sqllist.append(rows[i])
    return sqllist

# RENDERING THE CSV FILE AND ALLOWING TO ADD CHANNELS AND UPLOAD SUBMIT
def rendercsv(request, obj:VidSchool):
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file.save("Source/data/uploaded.csv")
            
            results = handlecsv("Source/data/uploaded.csv")
            
            channels = obj.get_channels()
            if results == None:
                return "Error: Invalid CSV"
            if channels == None:
                return "Error: No Channels"
            else:
                channellist = []
                for i in range(0, len(channels)):
                    channellist.append([channels[i][0],channels[i][1]])
            return flask.render_template("csv.html", list=results, channels=channellist, listurl="Source/data/uploaded.csv")
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# CHECKING THE CSV FILE FOR FORMATTING PROBLEMS
def csvchecker(list):
    print("running checker")
    if list[0][0] != "id":
        print("add header id")
    if list[0][1] != "title":
        print("add header title")
    if list[0][2] != "url":
        print("add header url")
    if list[0][3] != "shoot_timestamp":
        print("add header shoot_timestamp")
    if list[0][4] != "edit_timestamp":
        print("add header edit_timestamp")
    if list[0][5] != "upload_timestamp":
        print("add header upload_timestamp")
    if list[0][6] != "status":
        print("add header status")
    if list[0][7] != "comment":
        print("add header comment")
    for i in range(1, len(list)):
        if list[i][0] == "":
            return "add id in row " + str(i)
        if list[i][1] == "":
            return "add title in row " + str(i)
        if list[i][6] == "":
            return "add status in row " + str(i)
        if list[i][3] != "":
            try:
                datetime.datetime.strptime(list[i][3], "%d-%b-%y")
            except ValueError:
                return "invalid shoot_timestamp in row " + str(list[i][0])
        if list[i][4] != "":
            try:
                datetime.datetime.strptime(list[i][4], "%d-%b-%y")
            except ValueError:
                return "invalid edit_timestamp in row " + str(list[i][0])
        if list[i][5] != "":
            try:
                datetime.datetime.strptime(list[i][5], "%d-%b-%y")
            except ValueError:
                return "invalid upload_timestamp in row " + str(list[i][0])
    return True
    
# ADDING THE VIDEOS TO THE DATABASE
def csv2sql(request, obj:VidSchool, author):
    channel_id = request.form['channels']
    listurl = request.form['listurl']
    csvlist = handlecsv(listurl)
    print("triggered: ", channel_id, listurl)
    # csvlist = list(csvlist)
    # for i in csvlist:
    #     print(i)
    # return "Success"
    result = csvchecker(csvlist)
    if result != True:
        return result
    elif result == True:
        finallist = formatcsv(csvlist)
        obj.add_videos_bulk(finallist, channel_id, author=author)
        return flask.redirect(flask.url_for('view_videos'))

# Taking specific csvlist and formatting it for sql insertion
def formatcsv(csvlist):
    csvlist.remove(csvlist[0])
    final =[]
    for i in csvlist:
        for j in range(0, len(i)):
            if i[j] == "":
                i[j] = None
        id = i[0]
        title = i[1]
        url = i[2]
        shoot_timestamp = i[3]
        edit_timestamp = i[4]
        upload_timestamp = i[5]
        status = i[6]
        comment = i[7]
        if shoot_timestamp != None:
            shoot_timestamp = int(datetime.datetime.strptime(shoot_timestamp, "%d-%b-%y").timestamp())
        if edit_timestamp != None:
            edit_timestamp = int(datetime.datetime.strptime(edit_timestamp, "%d-%b-%y").timestamp())
        if upload_timestamp != None:
            upload_timestamp = int(datetime.datetime.strptime(upload_timestamp, "%d-%b-%y").timestamp())
        final.append([id, title, url, shoot_timestamp, edit_timestamp, upload_timestamp, status, comment])
    return final
        
        

# formatcsv(handlecsv("Source/data/uploaded.csv"))

# handlecsv("Source/data/formatted.csv")

