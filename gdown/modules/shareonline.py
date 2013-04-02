# -*- coding: utf-8 -*-

import re
import os

from ..core import browser


def upload(username, passwd, filename):
    """Returns uploaded file url."""
    file_size = int(os.path.getsize(filename))
    opera = browser()
    content = re.match('(.+);(.+)', opera.post('http://www.share-online.biz/upv3_session.php', {'username': username, 'password': passwd}).content)  # get upload_session and best server to upload
    upload_session = content.group(1)
    host = content.group(2)
    data = {'username': username, 'password': passwd, 'upload_session': upload_session, 'chunk_no': 1, 'chunk_number': 1, 'filesize': file_size, 'finalize': 1}
    content = opera.post('http://%s' % (host), data, files={'fn': open(filename, 'rb')}).content  # upload
    return re.match('(.+);[0-9]+;.+', content).group(1)
