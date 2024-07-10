from external_function import VidSchool
from datetime import datetime, date
import api_functions as api_functions
import requests

def get_main(channel_name, channel_id):
    # get cred for data
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return None
    print(data)
    # get total no. subscriptions, views and watchtime
    uploadsid = api_functions.youtubedata(
        'youtube',
        'v3',
        data,
        type='channel',
        part='snippet, contentDetails',
        mine=True,
        # mine=True,
    )
    print(uploadsid)
    uploadsid = uploadsid['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    today = datetime.now().strftime('%Y-%m-%d')
    stata = api_functions.youtubedata(
        'youtubeAnalytics', 
        'v2',
        credentials=data, 
        ids='channel==MINE',
        startDate='1990-01-01',
        metrics='subscribersGained,views,estimatedMinutesWatched',
        endDate=today,
    )
    print("stata done")
    # get total no. of videos
    statb = api_functions.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type="playlistItem",
        part='snippet',
        playlistId=uploadsid,
    )
    print("statb done")
    statb = statb['pageInfo']['totalResults']
    statc1 = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        ids='channel==MINE',
        startDate='1990-01-01',
        endDate=today,
        metrics='views',
        dimensions='video',
        maxResults=10,
        sort='-views',
    )
    print("statc1 done")
    top10vidlist = []
    for i in range(0,len(statc1['rows'])):
        top10vidlist.append(statc1['rows'][i][0])
    statc2 = api_functions.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type="video",
        part='snippet',
        id=",".join(top10vidlist),
    )
    statcfinal = []
    for i in range(0,len(statc1['rows'])):
        statcfinal.append({
            "name": statc2['items'][i]['snippet']['title'],
            "views": statc1['rows'][i][1],
        })
    print("statc2 done")
    # last_month = str(str(datetime.now().year-1)+'-'+str(datetime.now().month)+'-01')
    # todayd = str(datetime.now().year)+'-'+str(datetime.now().month-1)+'-01'
    statd1 = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        dimensions='month',
        ids='channel==MINE',
        metrics='views,estimatedMinutesWatched',
        startDate= date.today().replace(year=date.today().year-1,day=1).isoformat(),
        endDate=date.today().replace(day=1).isoformat(),
    )
    statdfinal = statd1['rows']
    print("statd1 done")
    return {
        "section_a":{
            "subscribers": stata['rows'][0][0],
            "views": stata['rows'][0][1],
            "watchtime": stata['rows'][0][2]/60,
        },
        "section_b":statb,
        "section_c":statcfinal,
        "section_d":statdfinal,
    }