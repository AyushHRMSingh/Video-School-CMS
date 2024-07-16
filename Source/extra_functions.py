import datetime
from type_vars import *

# function to turn credentials object into dictionary
def credtodict(cred):
    return {
        'token': cred.token,
        'refresh_token': cred.refresh_token,
        'token_uri': cred.token_uri,
        'client_id': cred.client_id,
        'client_secret': cred.client_secret,
        'scopes': cred.scopes
    }

# convert epoch to string
def epoch_to_string(epoch, type):
    if epoch == None:
        return ''
    if type == 'date':
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')
    elif type == 'datetime':
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

# convert string date into epoch
def string_to_epoch(string):
    if string != '':
        return int(datetime.datetime.strptime(string, '%Y-%m-%d').timestamp())
    else:
        return ''
    
# check whether or not a user is linked to the specified channel
def check_if_in_channel(user_type, user_id, channel):
    if user_type == USER_TYPE_CREATOR and user_id == channel[3]:
        return True
    elif user_type == USER_TYPE_EDITOR and user_id == channel[4]:
        return True
    elif user_type == USER_TYPE_OPS and user_id == channel[6]:
        return True
    elif user_type == USER_TYPE_MANAGER and user_id == channel[5]:
        return True
    elif user_type == USER_TYPE_ADMIN:
        return True
    else:
        return False
    