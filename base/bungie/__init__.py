#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import logging
import os
import re
import urlparse
from base.util import fetch


try:
  API_KEY = open('bungie.key').read().strip()
except:
  logging.exception('Unable to read API Key from "bungie.key" (see '
                    'https://www.bungie.net/en/Clan/Post/39966/85087279/0/0):')
  API_KEY = ''


BASE = 'https://www.bungie.net/platform/'


def Fetch(suffix, *args, **kwargs):
  if args:
    suffix %= args
  elif kwargs:
    suffix %= kwargs

  url = urlparse.urljoin(BASE, suffix)
  data = fetch.Fetch(url, headers={'X-API-Key': API_KEY})
  if isinstance(data, dict):
    if data.get('ErrorStatus') == 'Success':
      return data['Response']
  else:
    return data


def GetAvailableLocales():
  return Fetch('GetAvailableLocales/')


def HelloWorld():
  return Fetch('HelloWorld/')


def Settings():
  return Fetch('Settings/')


if __name__ == '__main__':
  assert HelloWorld() == 'Hello World'
  assert GetAvailableLocales()['English'] == 'en'
