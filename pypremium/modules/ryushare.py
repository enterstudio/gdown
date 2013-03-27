# -*- coding: utf-8 -*-

import requests
import datetime
import time
import re

from ..config import headers


def status(username, passwd):
    '''Returns account premium status:
    -999    unknown error
    -2      invalid password
    -1      account temporary blocked
    0       free account
    >0      premium date end timestamp'''
    opera = requests.session(headers=headers)
    content = opera.post('http://ryushare.com', {'op': 'login', 'redirect': 'http://ryushare.com/my-account.python', 'login': username, 'password': passwd, 'loginFormSubmit': 'Login'}).content
    if 'Your account was banned by administrator.' in content:
        return -1
    elif 'Incorrect Login or Password' in content:
        return -2
    elif any(i in content for i in ('Your IP was blocked because too many logins fail.', 'Your IP was had too many fail login!!!')):
        print 'ip blocked'
        ip_blocked
        return -101
    elif 'Premium account expire:' in content:
        return time.mktime(datetime.datetime.strptime(re.search('Premium account expire:</TD><TD><b>(.+)</b>', content).group(1), '%d %B %Y').timetuple())
    elif '<a class="logout" href="http://ryushare.com/logout">&nbsp;Logout</a>' in content:
        return 0
    else:
        open('log.log', 'w').write(content)
        print content
        new_status
        return -999
