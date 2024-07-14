import datetime

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

# function to turn response object to array/dictionary
def format_string(stringa):
    for i in stringa:
        # if detects special character that conflicts with javascript or any other syntax such as singlequote, doublequote, etc use \ to have it be ignored
        if i == "'":
            stringa = stringa.replace(i, "\'")
        if i == "\\":
            stringa = stringa.replace(i, "\\\\")

# render datetime function
def epoch_to_string(epoch, type):
    if epoch == None:
        return ''
    if type == 'date':
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')
    elif type == 'datetime':
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def string_to_epoch(string):
    if string != '':
        return int(datetime.datetime.strptime(string, '%Y-%m-%d').timestamp())
    else:
        return ''