# -*- coding: utf-8 -*-

import re
from datetime import datetime

from ..core import browser
from ..exceptions import ModuleError, IpBlocked, AccountBlocked, AccountRemoved


def getUrl(link, username, passwd):
    """Returns direct file url.
    IP validator is NOT present."""
    opera = browser()
    content = re.match('^https?://[w\.]{,4}rapidshare.com/files/([0-9]+)/(.+)$', link)
    fileid = content.group(1)
    filename = content.group(2)
    content = opera.get('https://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s&try=1&login=%s&password=%s' % (fileid, filename, username, passwd)).content
    server = re.match('DL:(.+?),', content).group(1)
    return opera.get('https://%s/cgi-bin/rsapi.cgi?sub=download&fileid=%s&filename=%s&try=0&login=%s&password=%s' % (server, fileid, filename, username, passwd)).url   # return connection


def expireDate(username, passwd):
    """Returns account premium expire date."""
    ''' List of errors:
    ERROR: Login failed. Password incorrect or account not found. (221a75e5)
    ERROR: Login failed. Account locked. Please contact us if you have questions. (b45c2518)
    ERROR: Login failed. Login data invalid. (0320f9f0)
    '''
    opera = browser()
    content = opera.get('https://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=getaccountdetails&login=%s&password=%s&withpublicid=1' % (username, passwd)).content
    if 'Login failed. Account locked.' in content:
        raise AccountBlocked
    elif 'Login failed. Password incorrect or account not found.' in content or 'Login failed. Login data invalid.' in content:
        raise AccountRemoved
    elif 'IP blocked' in content:   # ip blocked (too many wrong passwords)
        raise IpBlocked
    elif 'Login failed' in content:
        open('gdown.log', 'w').write(content)
        raise ModuleError('Unknown error, full log in gdown.log')
    elif 'billeduntil=' in content:
        # TODO: catch dates < now
        return datetime.fromtimestamp(re.search('billeduntil=(.+)\n', content).group(1))


def upload(username, passwd, filename):
    """Returns uploaded file url."""
    opera = browser()
    server_id = opera.get('https://api.rapidshare.com/cgi-bin/rsapi.cgi?sub=nextuploadserver').content
    content = opera.post('https://rs%s.rapidshare.com/cgi-bin/rsapi.cgi?sub=upload' % (server_id), {'login': username, 'password': passwd}, files={'filecontent': open(filename, 'rb')}).content
    file_id = re.search('([0-9]+),[0-9]+,.+', content).group(1)
    return 'https://rapidshare.com/files/%s/%s' % (file_id, filename)
