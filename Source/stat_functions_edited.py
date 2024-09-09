import math
from external_function import VidSchool
import datetime
import api_functions as api_functions
import requests

def get_default(channel_id):
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return None
    stata = get_basic_stats(data)
    statb = get_top_vids(data, 'alltime')
    statc = get_subscriber_stats(data, 'last_7_days')
    return {
        'section1': stata,
        'section2': statb,
        'section3': statc,
    }

def get_videos(channel_id, date_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_top_vids(data, date_range)
    }

def get_main(channel_id):
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return None
    stata = get_basic_stats(data)
    statb = get_top_vids(data)
    statc = get_subscriber_stats(data)
    return {
        'section1': stata,
        'section2': statb,
        'section3': statc,
    }

def get_basic_stats(data):
    basic_stat = api_functions.youtubedata(
        'youtube',
        'v3',
        data,
        type='channel',
        part='snippet,contentDetails,statistics',
        mine=True,
    )
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    watch_time = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        ids='channel==MINE',
        startDate='1990-01-01',
        endDate=today,
        metrics='estimatedMinutesWatched',
    )
    watch_time = watch_time['rows'][0][0]
    return {
        'url': basic_stat['items'][0]['snippet']["customUrl"],
        'view_Count': basic_stat['items'][0]['statistics']['viewCount'],
        'subscriber_Count': basic_stat['items'][0]['statistics']['subscriberCount'],
        'video_Count': basic_stat['items'][0]['statistics']['videoCount'],
        'watch_Time': math.floor(watch_time/60),
    }

def get_top_vids(data, date_range):
    oldest_date = '1990-01-01'
    today = datetime.date.today().isoformat()
    output = []

    if date_range == 'alltime':
        alltime = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=oldest_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(alltime['rows'])):
            output.append({
                'id': alltime['rows'][i][0],
                'views': alltime['rows'][i][1]
            })
    elif date_range == "last_7_days":
        last_7_days_date = (datetime.date.today()-datetime.timedelta(days=7)).isoformat()
        last_7_days = alltime = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=last_7_days_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(last_7_days['rows'])):
            output.append({
                'id': last_7_days['rows'][i][0],
                'views': last_7_days['rows'][i][1]
            })
    elif date_range == "last_30_days":
        last_30_days_date = (datetime.date.today()-datetime.timedelta(days=30)).isoformat()
        last_30_days = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=last_30_days_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(last_30_days['rows'])):
            output.append({
                'id': last_30_days['rows'][i][0],
                'views': last_30_days['rows'][i][1]
            })
    elif date_range == "last_90_days":
        last_90_days_date = (datetime.date.today()-datetime.timedelta(days=90)).isoformat()
        last_90_days = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=last_90_days_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(last_90_days['rows'])):
            output.append({
                'id': last_90_days['rows'][i][0],
                'views': last_90_days['rows'][i][1]
            })
    elif date_range == "last_6_months":
        last_6_month_date = (datetime.date.today()-datetime.timedelta(days=180)).isoformat()
        last_6_months = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=last_6_month_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(last_6_months['rows'])):
            output.append({
                'id': last_6_months['rows'][i][0],
                'views': last_6_months['rows'][i][1]
            })
    elif date_range == "past_year":
        last_year_date = (datetime.date.today()-datetime.timedelta(days=365)).isoformat()
        past_year = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            ids='channel==MINE',
            startDate=last_year_date,
            endDate=today,
            metrics='views',
            dimensions='video',
            maxResults=10,
            sort='-views',
        )
        for i in range(0,len(past_year['rows'])):
            output.append({
                'id': past_year['rows'][i][0],
                'views': past_year['rows'][i][1]
            })
    else:
        return None
    # get the videos
    print('\n\n\n\n\n de output')
    print(output)
    # for key in output:
    idlist = []
    for i in range(0,len(output)):
        idlist.append(output[i]['id'])
    stat_action = api_functions.youtubedata(
        'youtube',
        'v3',
        credentials=data,
        type="video",
        part='snippet',
        id=",".join(idlist),
    )
    for i in range(0,len(stat_action['items'])):
        output[i]['title'] = stat_action['items'][i]['snippet']['title']    
    return output

def get_subscriber_stats(data, date_range):
    
    raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
    today = raw_today.isoformat()
    this_month = raw_today.replace(month=raw_today.month-1, day=1)
    output = []
    print(date_range)
    if date_range == 'last_7_days':
        last_7_days_date = (raw_today-datetime.timedelta(days=6)).isoformat()
        
        # subsciber information for last 7 days
        last_7_days = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            dimensions='day',
            ids='channel==MINE',
            startDate=last_7_days_date,
            endDate=today,
            metrics='subscribersGained,subscribersLost',
        )
        
        # append to output
        for i in range(0, len(last_7_days['rows'])):
            output.append({
                'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
                'subscribersGained': last_7_days['rows'][i][1],
                'subscribersLost': last_7_days['rows'][i][2],
            })
        print(output)
        return output
    
    elif date_range == 'last_30_days':
        last_30_days_date = (raw_today-datetime.timedelta(days=29)).isoformat()
    
        # subsciber information for last 30 days
        last_30_days = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            dimensions='day',
            ids='channel==MINE',
            startDate=last_30_days_date,
            endDate=today,
            metrics='subscribersGained,subscribersLost',
        )
    
        # append to output
        for i in range(0, len(last_30_days['rows'])):
            output.append({
                'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
                'subscribersGained': last_30_days['rows'][i][1],
                'subscribersLost': last_30_days['rows'][i][2],
            })

        return output
    
    elif date_range == 'last_90_days':
        last_90_days_date = (raw_today-datetime.timedelta(days=89)).isoformat()

        # subsciber information for last 30 days
        last_90_days = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            dimensions='day',
            ids='channel==MINE',
            startDate=last_90_days_date,
            endDate=today,
            metrics='subscribersGained,subscribersLost',
        )

        # append to subs_list
        for i in range(0, len(last_90_days['rows'])):
            output.append({
                'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
                'subscribersGained': last_90_days['rows'][i][1],
                'subscribersLost': last_90_days['rows'][i][2],
            })
        
        return output
    
    elif date_range == 'last_6_months':
        last_6_month_date = (this_month-datetime.timedelta(days=150)).replace(day=1).isoformat()

        # return last_6_month_date
        last_6_months = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            dimensions='month',
            ids='channel==MINE',
            startDate=last_6_month_date,
            endDate=this_month,
            metrics='subscribersGained,subscribersLost',
        )
    
        # append to output
        for i in range(0, len(last_6_months['rows'])):
            output.append({
                'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
                'subscribersGained': last_6_months['rows'][i][1],
                'subscribersLost': last_6_months['rows'][i][2],
            })

        return output
    
    elif date_range == 'past_year':
        last_year_date = (this_month-datetime.timedelta(days=335)).replace(day=1).isoformat()
        
        # return past_year
        past_year = api_functions.youtubedata(
            'youtubeAnalytics',
            'v2',
            credentials=data,
            dimensions='month',
            ids='channel==MINE',
            startDate=last_year_date,
            endDate=this_month,
            metrics='subscribersGained,subscribersLost',
        )

        # append to output
        for i in range(0, len(past_year['rows'])):
            output.append({
                'date': dateconverstion(past_year['rows'][i][0], 'month'),
                'subscribersGained': past_year['rows'][i][1],
                'subscribersLost': past_year['rows'][i][2],
            })

        return output
    else:
        return None

def dateconverstion(datea, type):
    if type == 'day':
        return datetime.datetime.strptime(datea, '%Y-%m-%d').strftime('%d-%b')
    elif type == 'month':
        return datetime.datetime.strptime(datea, '%Y-%m').strftime('%b-%Y')