#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import json
import logging
import threading
import time
import urllib
import urllib2


_local = threading.local()


def Fetch(url, data=None, headers={}, tries=50):
  start = time.time()
  opener = getattr(_local, 'opener', None) or urllib2._opener or urllib2.build_opener()

  if isinstance(data, dict):
    data = urllib.urlencode(data)

  backoff = 1

  for i in xrange(tries):
    if i:
      time.sleep(backoff)
      backoff *= 2
      logging.error('Fetching %s (retry %i/%i).', url, i, tries - 1)

    try:
      req = urllib2.Request(url, data=data, headers=headers)
      conn = opener.open(req, timeout=backoff)
      content = conn.read()
    except:
      logging.exception('Exception while fetching %s:', url)
      continue

    content_type = conn.headers.get('content-type', 'text/plain').split(';')[0]
    if content_type == 'application/json':
      try:
        return json.loads(content)
      except:
        logging.exception('Exception while decoding %s: %r', url, content)
        continue

    return content

  logging.error('Failed to fetch %s (in %.3f s).', url, time.time() - start)


def SetOpener(opener):
  _local.opener = opener
