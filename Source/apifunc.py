import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

def youtdata():
    print("youtube data")
def youtanalytics():
    print("youtube analytics")
def youtreporting():
    print("youtube reporting")

def youtubedata(API_SERVICE_NAME, API_SERVICE_VERSION, credentials, **kwargs):
    # Build the service object.
    service = build(API_SERVICE_NAME, API_SERVICE_VERSION, credentials=credentials)

    # if analytics api
    if (API_SERVICE_NAME == 'youtubeAnalytics' and API_SERVICE_VERSION == 'v2'):
        request = service.reports().query(**kwargs)

    # if data api
    if (API_SERVICE_NAME == 'youtube' and API_SERVICE_VERSION == 'v3' and 'type' in kwargs):
        if kwargs['type'] == "channel":
            kwargs.pop('type')
            request = service.channels().list(**kwargs)
        elif kwargs['type'] == 'video':
            kwargs.pop('type')
            request = service.videos().list(**kwargs)
        elif kwargs['type'] == 'playlistItems':
            kwargs.pop('type')
            request = service.playlistItems().list(**kwargs)
    response = request.execute()
    
    return response