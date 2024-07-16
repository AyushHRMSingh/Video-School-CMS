import math
from external_function import VidSchool
from datetime import datetime, date
import api_functions as api_functions
import requests

def get_main(channel_name, channel_id):
    # get cred for data
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return None
    # print(data)
    # get total no. subscriptions, views and watchtime
    stata = api_functions.youtubedata(
        'youtube',
        'v3',
        data,
        type='channel',
        part='snippet,contentDetails,statistics',
        mine=True,
        # mine=True,
    )
    # print(stata)
    today = datetime.now().strftime('%Y-%m-%d')
    # get total watch time for whole life
    statb = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        ids='channel==MINE',
        startDate='1990-01-01',
        endDate=today,
        metrics='estimatedMinutesWatched',
    )
    print("statb done")
    statb = statb['rows'][0][0]
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
    current_month = date.today().replace(month=date.today().month-1,day=1).isoformat()
    last_year = date.today().replace(year=date.today().year-1,day=1).isoformat()
    statd1 = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        dimensions='month',
        ids='channel==MINE',
        metrics='views,estimatedMinutesWatched',
        startDate=last_year,
        endDate=current_month,
    )
    print(statd1)
    statdlist = []
    print(last_year)
    smonth = int(last_year[5:7])
    syear = int(last_year[0:4])
    for i in range(0,12):
        datef='{:04d}-{:02d}'.format(syear,smonth)
        if statd1['rows'][0][0] == datef:
            statdlist.append({
                "date":datef,
                "views":statd1['rows'][0][1],
                "watchtime":statd1['rows'][0][2],
            })
            statd1['rows'].pop(0)
        else:
            statdlist.append({
                "date":datef,
                "views":0,
                "watchtime":0,
            })
        if smonth == 12:
            smonth = 1
            syear += 1
        else:
            smonth +=1

    print(statdlist)
        # statdlist.append[{
        #     f'{last_year[5:7]}-{last_year[0:4],}':{
        #     }
        # }]

    return {
        "section_a":{
            'subscribers': stata['items'][0]['statistics']['subscriberCount'],
            'views': stata['items'][0]['statistics']['viewCount'],
            'totalvideos': stata['items'][0]['statistics']['videoCount'],
        },
        "section_b":math.floor(statb/60),
        "section_c":statcfinal,
        "section_d":statdlist
    }

def get_basic_stats(data):
    stata = api_functions.youtubedata(
        'youtube',
        'v3',
        data,
        type='channel',
        part='snippet,contentDetails,statistics',
        mine=True,
        # mine=True,
    )
    # print(stata)
    today = datetime.now().strftime('%Y-%m-%d')
    # get total watch time for whole life
    statb = api_functions.youtubedata(
        'youtubeAnalytics',
        'v2',
        credentials=data,
        ids='channel==MINE',
        startDate='1990-01-01',
        endDate=today,
        metrics='estimatedMinutesWatched',
    )
    print("statb done")
    statb = statb['rows'][0][0]

def get_top_vids(data):
    oldest_date = '1990-01-01'
    today = datetime.now().strftime('%Y-%m-%d')
    last_7_days_date = date.today().replace(day=date.today().day-7).isoformat()
    last_30_days_date = date.today().replace(day=date.today().day-30).isoformat()
    last_90_days_date = date.today().replace(day=date.today().day-90).isoformat()
    last_6_month_date = date.today().replace(month=date.today().month-6).isoformat()
    last_year_date = date.today().replace(year=date.today().year-1).isoformat()

    top_10_list = []
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

    # append to top_10_list
    all_time_list = []
    for i in range(0,len(alltime['rows'])):
        all_time_list.append(alltime['rows'][i][0])
    top_10_list.append(all_time_list)

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

    # append to top_10_list
    past_7_days_list = []
    for i in range(0,len(last_7_days['rows'])):
        past_7_days_list.append(last_7_days['rows'][i][0])
    top_10_list.append(past_7_days_list)

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
    past_30_days_list = []
    for i in range(0,len(last_30_days['rows'])):
        past_30_days_list.append(last_30_days['rows'][i][0])
    top_10_list.append(past_30_days_list)

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
    past_90_days_list = []
    for i in range(0,len(last_90_days['rows'])):
        past_90_days_list.append(last_90_days['rows'][i][0])
    top_10_list.append(past_90_days_list)

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
    past_6_months_list = []
    for i in range(0,len(last_6_months['rows'])):
        past_6_months_list.append(last_6_months['rows'][i][0])
    top_10_list.append(past_6_months_list)

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
    past_year_list = []
    for i in range(0,len(past_year['rows'])):
        past_year_list.append(past_year['rows'][i][0])
    top_10_list.append(past_year_list)


    final_result_list = []
    for i in top_10_list:
        stat_action = api_functions.youtubedata(
            'youtube',
            'v3',
            credentials=data,
            type="video",
            part='snippet',
            id=",".join(i),
        )

        templist = []
        for i in range(0,len(stat_action['rows'])):
            templist.append({
                "name": stat_action['items'][i]['snippet']['title'],
                "views": stat_action['rows'][i][1],
            })
        final_result_list.append(templist)
    return final_result_list






    # statc2 = api_functions.youtubedata(
    #     'youtube',
    #     'v3',
    #     credentials=data,
    #     type="video",
    #     part='snippet',
    #     id=",".join(top10vidlist),
    # )
    # statcfinal = []
    # for i in range(0,len(statc1['rows'])):
    #     statcfinal.append({
    #         "name": statc2['items'][i]['snippet']['title'],
    #         "views": statc1['rows'][i][1],
    #     })
    # print("statc2 done")