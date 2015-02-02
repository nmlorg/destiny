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
                    'https://www.bungie.net/en/Clan/39966):')
  API_KEY = ''


def _FetchWrap(path):
  return lambda self, **kwargs: self.Fetch(path, **kwargs)


class Bungie(object):
  base = 'https://www.bungie.net/platform/'

  def Fetch(self, suffix, *args, **kwargs):
    if args:
      suffix %= args
    elif kwargs:
      suffix %= kwargs

    url = urlparse.urljoin(self.base, suffix)
    data = fetch.Fetch(url, headers={'X-API-Key': API_KEY})
    if isinstance(data, dict):
      if data.get('ErrorStatus') == 'Success':
        return data['Response']
    else:
      return data

  for url in (
      'Destiny/%(accounttype)i/Account/%(accountid)i/',
      'Destiny/Manifest/',
      'GetAvailableLocales/',
      'GlobalAlert/',
      'HelloWorld/',
      'Settings/',
  ):
    methodname = re.sub('/%[(][^)]*[)][a-z]/', '/', url).replace('/', '')
    locals()[methodname] = _FetchWrap(url)


if __name__ == '__main__':
  bungie = Bungie()

  assert bungie.HelloWorld() == 'Hello World'
  assert bungie.GetAvailableLocales()['English'] == 'en'
  assert bungie.DestinyAccount(
      accounttype=2, accountid=4611686018436064455)['data']['characters'][0]['baseCharacterLevel'] == 20
