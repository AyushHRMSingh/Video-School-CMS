import time
import flask
import csv
from extfun import VidSchool
import datetime
import calendar

# FORMAT FOR CSV: [id, title, url, shoot_timestamp, edit_timestamp, upload_timestamp, comment]

# set of drop in functions for flask

# Function that takes the location of the csv file and returns a list of the csv file
def handlecsv(url):
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

# Functions that takes the csv file, verifies it, presents it with option to select channel type and submit button to add to database
def rendercsv(request, obj:VidSchool):
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # save file to location
            file.save("Source/data/uploaded.csv")
            # get the csv file as a list
            results = handlecsv("Source/data/uploaded.csv")
            # get channel
            channels = obj.get_channels()
            # return error if problems with csv or no channels to select
            if results == None:
                return "Error: Invalid CSV"
            if channels == None:
                return "Error: No Channels"
            else:
                channellist = []
                # add channel id and names togather as one item in list for dropdown
                for i in range(0, len(channels)):
                    channellist.append([channels[i][0],channels[i][1]])
            # render html file with channels and csvfile
            return flask.render_template("csv.html", list=results, channels=channellist, listurl="Source/data/uploaded.csv")
    # default output page asking for upload
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
    # check if all header values are present, not necessary but good practice
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

    # check if all rows have valid values in the important places
    for i in range(1, len(list)):
        # id check
        if list[i][0] == "":
            return "add id in row " + str(i)
        # title check
        if list[i][1] == "":
            return "add title in row " + str(i)
        # status check
        if list[i][6] == "":
            return "add status in row " + str(i)
        # shoot_timestamp check
        if list[i][3] != "":
            try:
                datetime.datetime.strptime(list[i][3], "%d-%b-%y")
            except ValueError:
                return "invalid shoot_timestamp in row " + str(list[i][0])
        # edit_timestamp check
        if list[i][4] != "":
            try:
                datetime.datetime.strptime(list[i][4], "%d-%b-%y")
            except ValueError:
                return "invalid edit_timestamp in row " + str(list[i][0])
        # upload_timestamp check
        if list[i][5] != "":
            try:
                datetime.datetime.strptime(list[i][5], "%d-%b-%y")
            except ValueError:
                return "invalid upload_timestamp in row " + str(list[i][0])
    return True
    
# Takes the csv list and prepares it for insertion into the database
def formatcsv(csvlist):
    # remove the header row
    csvlist.remove(csvlist[0])
    for i in csvlist:
        for j in range(0, len(i)):
            # replaces empty string values so output is NULL in database
            if i[j] == "":
                i[j] = None
        # for non empty dates convert to epoch timestamp
        # shoot_timestamp
        if i[3] != None:
            i[3] = int(datetime.datetime.strptime(i[3], "%d-%b-%y").timestamp())
        # edit_timestamp
        if i[4] != None:
            i[4] = int(datetime.datetime.strptime(i[4], "%d-%b-%y").timestamp())
        # upload_timestamp
        if i[5] != None:
            i[5] = int(datetime.datetime.strptime(i[5], "%d-%b-%y").timestamp())
    return csvlist
        
# ADDING THE VIDEOS TO THE DATABASE
def csv2sql(request, obj:VidSchool, author):
    # get channel_id, listurl and get csvlist
    channel_id = request.form['channels']
    listurl = request.form['listurl']
    csvlist = handlecsv(listurl)
    # check if csv is valid
    result = csvchecker(csvlist)
    if result != True:
        return result
    elif result == True:
        # format csv and add to database
        finallist = formatcsv(csvlist)
        obj.add_videos_bulk(finallist, channel_id, author=author)
        return flask.redirect(flask.url_for('view_videos'))        

# formatcsv(handlecsv("Source/data/uploaded.csv"))

# handlecsv("Source/data/formatted.csv")

