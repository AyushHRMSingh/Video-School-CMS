import time
from googleapiclient.discovery import build
import google.oauth2.credentials
import requests

def refresh_token(old_credentials):
    data = {
        "client_id": old_credentials['client_id'],
        "client_secret": old_credentials['client_secret'],
        "refresh_token": old_credentials['refresh_token'],
        "grant_type": "refresh_token"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    new_tokens = response.json()
    new_access_token = new_tokens.get("access_token")
    expiry = time.time()+new_tokens.get("expires_in")
    newcred = {
        'client_id': old_credentials['client_id'],
        'client_secret': old_credentials['client_secret'],
        'refresh_token': old_credentials['refresh_token'],
        'scopes': old_credentials['scopes'],
        'token_uri': old_credentials['token_uri'],
        'token': new_access_token
    }
    return [newcred, expiry]

def youtdata():
    print("youtube data")
def youtanalytics():
    print("youtube analytics")
def youtreporting():
    print("youtube reporting")

def youtubedata(API_SERVICE_NAME, API_SERVICE_VERSION, credentials, **kwargs):
    # print("Stuff: ",API_SERVICE_NAME, API_SERVICE_VERSION, credentials, kwargs)
    # Build the service object.
    credentials = google.oauth2.credentials.Credentials(**credentials)
    service = build(API_SERVICE_NAME, API_SERVICE_VERSION, credentials=credentials)

    # if analytics api
    if (API_SERVICE_NAME == 'youtubeAnalytics' and API_SERVICE_VERSION == 'v2'):
        request = service.reports().query(**kwargs)

    # if data api
    elif (API_SERVICE_NAME == 'youtube' and API_SERVICE_VERSION == 'v3' and 'type' in kwargs):
        args = kwargs
        # print(args['type'], args)
        if args['type'] == "channel":
            args.pop('type')
            # print(args)
            request = service.channels().list(**args)
        elif args['type'] == 'video':
            args.pop('type')
            # print(args)
            request = service.videos().list(**args)
        elif args['type'] == 'playlistItem':
            args.pop('type')
            # print(args)
            request = service.playlistItems().list(**args)
    response = request.execute()
    # print("response:-")
    # print(response)
    return response