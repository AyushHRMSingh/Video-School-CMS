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
def formatresa(res):
    print(res)
    newres = []
    for i in range(0,len(res['columnHeaders'])):
        newres.append({
            'metric': res['columnHeaders'][i]['name'],
            'data': res['rows'][0][i]
        })
    return newres