#!/usr/bin/python
#
# Copyright 2015 Daniel Reed <n@ml.org>

import cookielib
import urllib
import urllib2


try:
  API_KEY = open('bungie.key').read().strip()
except:
  logging.exception('Unable to read API Key from "bungie.key" (see '
                    'https://www.bungie.net/en/Clan/Post/39966/85087279/0/0):')
  API_KEY = ''


def Auth(username, password):
  bungie_url = 'https://www.bungie.net/en/User/SignIn/Psnid'
  psn_url = 'https://auth.api.sonyentertainmentnetwork.com/login.do'

  jar = cookielib.CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

  req = urllib2.Request(bungie_url)
  conn = opener.open(req)
  _ = conn.read()

  req = urllib2.Request(
      psn_url, data=urllib.urlencode({'j_username': username, 'j_password': password}))
  conn = opener.open(req)
  _ = conn.read()

  opener.add_handler(HeaderAdder({
      'x-api-key': API_KEY,
      'x-csrf': jar._cookies['www.bungie.net']['/']['bungled'].value,
  }))

  return opener


class HeaderAdder(urllib2.BaseHandler):
  def __init__(self, headers):
    self.headers = headers

  def https_request(self, req):
    for k, v in self.headers.iteritems():
      req.add_header(k, v)
    return req
