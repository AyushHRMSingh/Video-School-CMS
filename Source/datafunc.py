from extfun import VidSchool
from datetime import datetime
import apifunc
import requests

def get_main(vobj:VidSchool, channel_name):
    # get cred for data
    credential = vobj.get_token()
    data = credential['credentials']
    # get access token
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    access_token = response.json().get('access_token')
    data['access_token'] = access_token
    # get total no. subscriptions, views and watchtime
    uploadsid = apifunc.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type='playlistItems',
        part='contentDetails',
        forUsername=channel_name,
    )
    uploadsid = uploadsid['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    today = datetime.now().strftime('%Y-%m-%d')
    stata = apifunc.youtubedata(
        'youtubeAnalytics', 
        'v2',
        credentials=data, 
        ids='channel==MINE',
        startDate='1990-01-01',
        endDate=today,
    )
    # get total no. of videos
    statb = apifunc.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type="channel",
        part='snippet',
        playlistId=uploadsid,
    )
    statb = statb['pageInfo']['totalResults']
    statc1 = apifunc.youtubedata(
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
    top10vidlist = []
    for i in range(0,len(statc1['rows'])):
        top10vidlist.append(statc1['rows'][i][0])
    statc2 = apifunc.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type="channel",
        part='snippet',
        id=top10vidlist,
    )
    statcfinal = []
    for i in range(0,len(statc1['rows'])):
        statcfinal.append({
            "name": statc2['items'][i]['snippet']['title'],
            "views": statc1['rows'][i][1],
        })
    statd1 = apifunc.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        dimensions='month',
        ids='channel==MINE',
        metrics='views,estimatedMinutesWatched',
        startDate=(datetime.now().year-1)+'-'+datetime.now().month+'-01',
        endDate=datetime.now().year+'-'+datetime.now().month+'-01',
    )
    return {
        "section_a":stata,
        "section_b":statb,
        "section_c":statcfinal,
    }