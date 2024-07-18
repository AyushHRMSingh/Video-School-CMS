import math
from external_function import VidSchool
import datetime
import api_functions as api_functions
import requests

def get_main(channel_id):
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return None
    stata = get_basic_stats(data)
    statb = get_top_vids(data)
    statc = get_subscriber_status(data)
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
        'watch_time': math.floor(watch_time/60),
    }

def get_top_vids(data):
    oldest_date = '1990-01-01'
    today = datetime.date.today().isoformat()
    last_7_days_date = (datetime.date.today()-datetime.timedelta(days=7)).isoformat()
    last_30_days_date = (datetime.date.today()-datetime.timedelta(days=30)).isoformat()
    last_90_days_date = (datetime.date.today()-datetime.timedelta(days=90)).isoformat()
    last_6_month_date = (datetime.date.today()-datetime.timedelta(days=180)).isoformat()
    last_year_date = (datetime.date.today()-datetime.timedelta(days=365)).isoformat()

    top_10_list = {}
    # top 10 videos all time
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
    
    top_10_list['alltime'] = []
    for i in range(0,len(alltime['rows'])):
        top_10_list['alltime'].append({
            'id': alltime['rows'][i][0],
            'views': alltime['rows'][i][1]
        })

    # top 10 videos last 7 days
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

    top_10_list['last_7_days'] = []
    for i in range(0,len(last_7_days['rows'])):
        top_10_list['last_7_days'].append({
            'id': last_7_days['rows'][i][0],
            'views': last_7_days['rows'][i][1]
        })

    # top 10 videos last 30 days
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

    # append to top_10_list
    top_10_list['last_30_days'] = []
    for i in range(0,len(last_30_days['rows'])):
        top_10_list['last_30_days'].append({
            'id': last_30_days['rows'][i][0],
            'views': last_30_days['rows'][i][1]
        })

    # top 10 videos last 90 days
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

    # append to top_10_list
    top_10_list['last_90_days'] = []
    for i in range(0,len(last_90_days['rows'])):
        top_10_list['last_90_days'].append({
            'id': last_90_days['rows'][i][0],
            'views': last_90_days['rows'][i][1]
        })

    # top 10 videos last 6 months
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

    # append to top_10_list
    top_10_list['last_6_months'] = []
    for i in range(0,len(last_6_months['rows'])):
        top_10_list['last_6_months'].append({
            'id': last_6_months['rows'][i][0],
            'views': last_6_months['rows'][i][1]
        })

    # top 10 videos past year
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

    # append to top_10_list
    top_10_list['past_year'] = []
    for i in range(0,len(past_year['rows'])):
        top_10_list['past_year'].append({
            'id': past_year['rows'][i][0],
            'views': past_year['rows'][i][1]
        })

    for key in top_10_list:
        idlist = []
        for i in range(0,len(top_10_list[key])):
            idlist.append(top_10_list[key][i]['id'])
        stat_action = api_functions.youtubedata(
            'youtube',
            'v3',
            credentials=data,
            type="video",
            part='snippet',
            id=",".join(idlist),
        )
        for i in range(0,len(stat_action['items'])):
            top_10_list[key][i]['title'] = stat_action['items'][i]['snippet']['title']    

    return top_10_list

def get_subscriber_status(data):
    
    raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
    today = raw_today.isoformat()
    this_month = raw_today.replace(month=raw_today.month-1, day=1)

    # return (today, oldest_date)
    last_7_days_date = (raw_today-datetime.timedelta(days=6)).isoformat()
    last_30_days_date = (raw_today-datetime.timedelta(days=29)).isoformat()
    last_90_days_date = (raw_today-datetime.timedelta(days=89)).isoformat()
    last_6_month_date = (this_month-datetime.timedelta(days=150)).replace(day=1).isoformat()
    last_year_date = (this_month-datetime.timedelta(days=335)).replace(day=1).isoformat()

    # return ([
    #     this_month,
    #     last_6_month_date
    # ])

    subs_list = {}

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

    # return last_7_days

    # print(last_7_days)

    # append to subs_list
    subs_list['last_7_days'] = []
    for i in range(0, len(last_7_days['rows'])):
        subs_list['last_7_days'].append({
            'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
            'subscribersGained': last_7_days['rows'][i][1],
            'subscribersLost': last_7_days['rows'][i][2],
        })


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

    # append to subs_list
    subs_list['last_30_days'] = []
    for i in range(0, len(last_30_days['rows'])):
        subs_list['last_30_days'].append({
            'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
            'subscribersGained': last_30_days['rows'][i][1],
            'subscribersLost': last_30_days['rows'][i][2],
        })

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
    subs_list['last_90_days'] = []
    for i in range(0, len(last_90_days['rows'])):
        subs_list['last_90_days'].append({
            'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
            'subscribersGained': last_90_days['rows'][i][1],
            'subscribersLost': last_90_days['rows'][i][2],
        })


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

    # return last_6_months

    # append to subs_list
    subs_list['last_6_months'] = []
    for i in range(0, len(last_6_months['rows'])):
        subs_list['last_6_months'].append({
            'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
            'subscribersGained': last_6_months['rows'][i][1],
            'subscribersLost': last_6_months['rows'][i][2],
        })
    
    

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

    # append to subs_list
    subs_list['past_year'] = []
    for i in range(0, len(past_year['rows'])):
        subs_list['past_year'].append({
            'date': dateconverstion(past_year['rows'][i][0], 'month'),
            'subscribersGained': past_year['rows'][i][1],
            'subscribersLost': past_year['rows'][i][2],
        })

    return subs_list


def dateconverstion(datea, type):
    if type == 'day':
        return datetime.datetime.strptime(datea, '%Y-%m-%d').strftime('%d-%b')
    elif type == 'month':
        return datetime.datetime.strptime(datea, '%Y-%m').strftime('%b-%Y')