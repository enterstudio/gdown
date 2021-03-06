# -*- coding: utf-8 -*-

"""
gdown.modules.turbobit
~~~~~~~~~~~~~~~~~~~

This module contains handlers for turbobit.

"""

import re
from dateutil import parser

from ..core import recaptcha, recaptchaReportWrong
from ..module import browser, acc_info_template
from ..exceptions import ModuleError

recaptcha_public_key = '6LcTGLoSAAAAAHCWY9TTIrQfjUlxu6kZlTYP50_c'


def getUrl(link, username, passwd):
    """Returns direct file url."""
    r = browser()
    values = {'user[login]': username, 'user[pass]': passwd, 'user[memory]': '1', 'user[submit]': 'Login'}
    r.post('http://turbobit.net/user/login', values)
    content = r.get(link).content
    link = re.search("<h1><a href='(.+)'>", content).group(1)
    return r.get(link).url  # return connection


def upload(username, passwd, filename):
    """Returns uploaded file url."""
    #file_size = os.path.getsize(filename)  # get file size
    r = browser()
    values = {'user[login]': username, 'user[pass]': passwd, 'user[memory]': '1', 'user[submit]': 'Login'}
    r.post('http://turbobit.net/user/login', values).content  # login
    content = r.get('http://turbobit.net/').content
    content = re.search('urlSite=(http://s[0-9]+.turbobit.ru/uploadfile)&userId=(.+)&', content)
    host = content.group(1)
    user_id = content.group(2)
    content = r.post(host, {'Filename': filename, 'user_id': user_id, 'stype': 'null', 'apptype': 'fd1', 'id': 'null', 'Upload': 'Submit Query'}, files={'Filedata': open(filename, 'rb')}).content  # upload
    file_id = re.search('{"result":true,"id":"(.+)","message":"Everything is ok"}', content).group(1)
    return 'http://turbobit.net/%s.html' % (file_id)


def accInfo(username, passwd, captcha=False, proxy=False):
    """Returns account info."""
    acc_info = acc_info_template()
    r = browser(proxy)
    values = {'user[login]': username, 'user[pass]': passwd, 'user[memory]': '1', 'user[submit]': 'Login'}
    if captcha:
        recaptcha_challenge, recaptcha_response = recaptcha(recaptcha_public_key)
        values['recaptcha_challenge_field'] = recaptcha_challenge
        values['recaptcha_response_field'] = recaptcha_response
        values['user[captcha_type]'] = 'recaptcha'
        values['user[captcha_subtype]'] = ''
    r.headers['Referer'] = 'http://turbobit.net/login'
    content = r.post('http://turbobit.net/user/login', values).content  # login
    if captcha and 'Incorrect captcha code' in content:
        recaptchaReportWrong()  # add captcha_id
        return accInfo(username, passwd, captcha=True, proxy=proxy)
    elif any(i in content for i in ('Incorrect login or password', 'E-Mail address appears to be invalid. Please try again', 'Username(Email) does not exist')):
        acc_info['status'] = 'deleted'
        return acc_info
    elif 'Limit of login attempts exceeded for your account. It has been temporarily locked.' in content:
        acc_info['status'] = 'blocked'
        return acc_info
    elif 'Limit of login attempts exeeded.' in content or 'Please enter the captcha.' in content:
        return accInfo(username, passwd, captcha=True, proxy=proxy)
    # TODO: use if (check value) instead of try-except
    elif 'Turbo access denied' in content:
        acc_info['status'] = 'free'
        return acc_info
    elif 'Turbo access till' in content:
        content = re.search("<span class='note'>Turbo access till ([0-9]{2}\.[0-9]{2}\.[0-9]{4})</span>", content).group(1)
        acc_info['status'] = 'premium'
        acc_info['expire_date'] = parser.parse(content, dayfirst=True)
        return acc_info
'''
    try:
        content = re.search('<u>Turbo Access</u> [to ]{,3}(.*?)\.?[	]+</div>', content).group(1)
    except:
        open('gdown.log', 'w').write(content)
        raise ModuleError('Unknown error, full log in gdown.log')
    if content == 'denied':
        acc_info['status'] = 'free'
        return acc_info
    else:
        acc_info['status'] = 'premium'
        acc_info['expire_date'] = parser.parse(content, dayfirst=True)
        return acc_info
'''
