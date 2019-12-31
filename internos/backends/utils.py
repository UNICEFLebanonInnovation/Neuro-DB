import json
import httplib
import datetime
from time import mktime


def get_data(url, apifunc, token, protocol='HTTPS'):

    headers = {"Content-type": "application/json",
               "Authorization": token,
               "HTTP_REFERER": "etools.unicef.org",
               # "Cookie": "tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I",
               # "X-CSRFToken": 'tfUDK97TJSCkB4Nlm2wuMx67XNOYWpKT18BeV3RNoeq6nO7FXemAZypct369yF9I',
               # "username": "achamseddine@unicef.org", "password": "Alouche21!"
               }

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)
    conn.request('GET', apifunc, "", headers)
    response = conn.getresponse()
    result = response.read()

    if not response.status == 200:
        if response.status == 400 or response.status == 403:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result
