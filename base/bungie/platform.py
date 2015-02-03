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
      'Destiny/%(accounttype)i/Account/%(accountid)i/Character/%(characterid)i/Inventory/',
      'Destiny/%(accounttype)i/Account/%(accountid)i/Character/%(characterid)i/Progression/',
      'Destiny/Manifest/',
      'Destiny/SearchDestinyPlayer/%(accounttype)s/%(name)s/',
      'Destiny/Stats/ActivityHistory/%(accounttype)i/%(accountid)i/%(characterid)i/?mode=0&count=%(count)i',
      'Destiny/Stats/PostGameCarnageReport/%(activityid)i/',
      'GetAvailableLocales/',
      'GlobalAlert/',
      'HelloWorld/',
      'Settings/',
  ):
    methodname = re.sub('%[(][^)]*[)][a-z]/', '', url.split('?', 1)[0]).replace('/', '')
    locals()[methodname] = _FetchWrap(url)


if __name__ == '__main__':
  bungie = Bungie()

  assert bungie.HelloWorld() == 'Hello World'
  assert bungie.GetAvailableLocales()['English'] == 'en'
  assert bungie.DestinyAccount(
      accounttype=2, accountid=4611686018436064455)['data']['characters'][0]['baseCharacterLevel'] == 20
