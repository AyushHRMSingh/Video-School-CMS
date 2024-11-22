import math
from external_function import VidSchool
import datetime
import api_functions as api_functions

def get_default(channel_id):
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return {}
    stat_a = get_basic_stats(data)
    stat_b = get_top_vids(data, 'alltime')
    stat_c = get_subscriber_stats(data, 'last_7_days')
    stat_d = get_likes_stats(data, 'last_7_days')
    stat_e = get_average_view_duration_stats(data, 'last_7_days')
    stat_f = get_cpm_stats(data, 'last_7_days')
    stat_g = get_shares_stats(data, 'last_7_days')
    return {
        'base': stat_a,
        'topVideos': stat_b,
        'subscriberData': stat_c,
        'likeData': stat_d,
        'averageViewDuration': stat_e,
        'cpmData': stat_f,
        'sharesData': stat_g,
    }

# function to get the top videos
def get_videos(channel_id, date_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_top_vids(data, date_range)
    }

# function to get the subscriber stats
def get_subscribers(channel_id, date_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_subscriber_stats(data, date_range)
    }

def get_main(channel_id):
    data = VidSchool.get_credentials(channel_id=channel_id)
    if data == None:
        return {}
    stata = get_basic_stats(data)
    statb = get_top_vids(data)
    statc = get_subscriber_stats(data)
    return {
        'section1': stata,
        'section2': statb,
        'section3': statc,
    }

def get_likes(channel_id, date_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_likes_stats(data, date_range)
    }

def get_average_view_duration(channel_id, date_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_average_view_duration_stats(data, date_range)
    }

def get_cpm(channel_id, data_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_cpm_stats(data, data_range)
    }

def get_shares(channel_id, data_range):
    data = VidSchool.get_credentials(channel_id=channel_id)
    return {
        'data' : get_shares_stats(data, data_range)
    }

### BACK FUNCTIONS (NOT FOR DIRECT CALLS)

# function to get some base stats such as view count, subscriber count, video count, watch time
def get_basic_stats(data):
    try:
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
    except Exception as e:
        print(e)
        return {}

# function to get top videos associated with a youtube channel
def get_top_vids(data, date_range):
    try:
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
            return {}
        
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
    except Exception as e:
        print(e)
        return {}

# function to get subscriber stats over time associated with a youtube channel
def get_subscriber_stats(data, date_range):
    try:
        raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
        today = raw_today.isoformat()
        this_month = raw_today.replace(month=raw_today.month-1, day=1)
        output = []
        # print(date_range)
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
            # print(output)
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
            return {}
    except Exception as e:
        print(e)
        return {}

# function to get likes stats over time associated with a youtube channel
def get_likes_stats(data, date_range):
    try:
        raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
        today = raw_today.isoformat()
        this_month = raw_today.replace(month=raw_today.month-1, day=1)
        output = []
        # print(date_range)
        
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
                metrics='likes',
            )
            
            # append to output
            for i in range(0, len(last_7_days['rows'])):
                output.append({
                    'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
                    'likes': last_7_days['rows'][i][1],
                })
            # print(output)
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
                metrics='likes',
            )
        
            # append to output
            for i in range(0, len(last_30_days['rows'])):
                output.append({
                    'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
                    'likes': last_30_days['rows'][i][1],
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
                metrics='likes',
            )

            # append to subs_list
            for i in range(0, len(last_90_days['rows'])):
                output.append({
                    'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
                    'likes': last_90_days['rows'][i][1],
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
                metrics='likes',
            )
        
            # append to output
            for i in range(0, len(last_6_months['rows'])):
                output.append({
                    'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
                    'likes': last_6_months['rows'][i][1],
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
                metrics='likes',
            )

            # append to output
            for i in range(0, len(past_year['rows'])):
                output.append({
                    'date': dateconverstion(past_year['rows'][i][0], 'month'),
                    'likes': past_year['rows'][i][1],
                })

            return output
        
        else:
            return {}
    except Exception as e:
        print(e)
        return {}

# function to get the average view duration stats over time associated with a youtube channel
def get_average_view_duration_stats(data, date_range):
    try:
        raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
        today = raw_today.isoformat()
        this_month = raw_today.replace(month=raw_today.month-1, day=1)
        output = []
        # print(date_range)
        
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
                metrics='averageViewDuration',
            )
            
            # append to output
            for i in range(0, len(last_7_days['rows'])):
                output.append({
                    'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
                    'averageViewDuration': last_7_days['rows'][i][1],
                })
            # print(output)
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
                metrics='averageViewDuration',
            )
        
            # append to output
            for i in range(0, len(last_30_days['rows'])):
                output.append({
                    'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
                    'averageViewDuration': last_30_days['rows'][i][1],
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
                metrics='averageViewDuration',
            )

            # append to subs_list
            for i in range(0, len(last_90_days['rows'])):
                output.append({
                    'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
                    'averageViewDuration': last_90_days['rows'][i][1],
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
                metrics='averageViewDuration',
            )
        
            # append to output
            for i in range(0, len(last_6_months['rows'])):
                output.append({
                    'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
                    'averageViewDuration': last_6_months['rows'][i][1],
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
                metrics='averageViewDuration',
            )

            # append to output
            for i in range(0, len(past_year['rows'])):
                output.append({
                    'date': dateconverstion(past_year['rows'][i][0], 'month'),
                    'averageViewDuration': past_year['rows'][i][1],
                })

            return output
        
        else:
            return {}
    except Exception as e:
        print(e)
        return {}

def get_cpm_stats(data, date_range):
    try:
        raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
        today = raw_today.isoformat()
        this_month = raw_today.replace(month=raw_today.month-1, day=1)
        output = []
        # print(date_range)
        
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
                metrics='cpm',
            )
            
            # append to output
            for i in range(0, len(last_7_days['rows'])):
                output.append({
                    'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
                    'cpm': last_7_days['rows'][i][1],
                })
            # print(output)
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
                metrics='cpm',
            )
        
            # append to output
            for i in range(0, len(last_30_days['rows'])):
                output.append({
                    'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
                    'cpm': last_30_days['rows'][i][1],
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
                metrics='cpm',
            )

            # append to subs_list
            for i in range(0, len(last_90_days['rows'])):
                output.append({
                    'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
                    'cpm': last_90_days['rows'][i][1],
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
                metrics='cpm',
            )
        
            # append to output
            for i in range(0, len(last_6_months['rows'])):
                output.append({
                    'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
                    'cpm': last_6_months['rows'][i][1],
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
                metrics='cpm',
            )

            # append to output
            for i in range(0, len(past_year['rows'])):
                output.append({
                    'date': dateconverstion(past_year['rows'][i][0], 'month'),
                    'cpm': past_year['rows'][i][1],
                })
            # print(output)
            return output
        
        else:
            return {}
    except Exception as e:
        print(e)
        return {}

def get_shares_stats(data, date_range):
    
    try:
        raw_today = (datetime.datetime.now()-datetime.timedelta(days=3)).date()
        today = raw_today.isoformat()
        this_month = raw_today.replace(month=raw_today.month-1, day=1)
        output = []
        # print(date_range)
        
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
                metrics='shares',
            )
            
            # append to output
            for i in range(0, len(last_7_days['rows'])):
                output.append({
                    'date': dateconverstion(last_7_days['rows'][i][0], 'day'),
                    'shares': last_7_days['rows'][i][1],
                })
            # print(output)
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
                metrics='shares',
            )
        
            # append to output
            for i in range(0, len(last_30_days['rows'])):
                output.append({
                    'date': dateconverstion(last_30_days['rows'][i][0], 'day'),
                    'shares': last_30_days['rows'][i][1],
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
                metrics='shares',
            )

            # append to subs_list
            for i in range(0, len(last_90_days['rows'])):
                output.append({
                    'date': dateconverstion(last_90_days['rows'][i][0], 'day'),
                    'shares': last_90_days['rows'][i][1],
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
                metrics='shares',
            )
        
            # append to output
            for i in range(0, len(last_6_months['rows'])):
                output.append({
                    'date': dateconverstion(last_6_months['rows'][i][0], 'month'),
                    'shares': last_6_months['rows'][i][1],
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
                metrics='shares',
            )

            # append to output
            for i in range(0, len(past_year['rows'])):
                output.append({
                    'date': dateconverstion(past_year['rows'][i][0], 'month'),
                    'shares': past_year['rows'][i][1],
                })
            print(output)
            return output
        
        else:
            return {}
    except Exception as e:
        print(e)
        return {}

# function to convert date to a specific format
def dateconverstion(datea, type):
    if type == 'day':
        return datetime.datetime.strptime(datea, '%Y-%m-%d').strftime('%d-%b')
    elif type == 'month':
        return datetime.datetime.strptime(datea, '%Y-%m').strftime('%b-%Y')
