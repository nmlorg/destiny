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

  return (jar._cookies['www.bungie.net']['/']['bungled'].value,
          jar._cookies['www.bungie.net']['/']['bungleatk'].value)


def BuildOpener(bungled, bungleatk):
  opener = urllib2.build_opener()
  jar = cookielib.CookieJar()
  jar.set_cookie(BungieCookie('bungled', bungled))
  jar.set_cookie(BungieCookie('bungleatk', bungleatk))
  opener.add_handler(urllib2.HTTPCookieProcessor(jar))
  opener.extra_headers = {'x-api-key': API_KEY, 'x-csrf': bungled}
  opener.add_handler(HeaderAdder(opener.extra_headers))
  return opener


def BungieCookie(name, value):
  return cookielib.Cookie(
      version=0, name=name, value=value, port=None, port_specified=False, domain='www.bungie.net',
      domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=True,
      expires=None, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None},
      rfc2109=False)


class HeaderAdder(urllib2.BaseHandler):
  def __init__(self, headers):
    self.headers = headers

  def https_request(self, req):
    for k, v in self.headers.iteritems():
      req.add_header(k, v)
    return req
