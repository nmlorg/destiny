#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import fetch


_BASE = 'https://www.bungie.net/Platform/Destiny'


def Fetch(suffix, *args, **kwargs):
  if args:
    suffix %= args
  elif kwargs:
    suffix %= kwargs

  url = _BASE + suffix
  if '?' in url:
    url += '&'
  else:
    url += '?'
  url += 'definitions=true'
  data = fetch.Fetch(url)
  if data.get('ErrorStatus') == 'Success':
    return data['Response']


class Definitions(dict):
  def __init__(self, data=None):
    if data:
      self.update(data)

  def update(self, data):
    for code, d in data.get('items', {}).iteritems():
      self[long(code)] = {
          'name': d['itemName'].strip(),
          'desc': d.get('itemDescription', '').strip(),
          'icon': d['icon'].strip(),
      }

  def __missing__(self, k):
    return {'name': '#%i' % k}

  def Fetch(self, suffix, *args, **kwargs):
    ret = Fetch(suffix, *args, **kwargs)
    if ret:
      self.update(ret['definitions'])
      return ret['data']


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None, defs=None):
    if defs is None:
      defs = Definitions()
    self.defs = defs

    if accounttype is None or accountid is None:
      if not accounttype:
        accounttype = 'All'
      data = Fetch('/SearchDestinyPlayer/%s/%s/', accounttype, username)
      assert data and len(data) == 1, data
      username = data[0]['displayName']
      accounttype = long(data[0]['membershipType'])
      accountid = long(data[0]['membershipId'])

    assert isinstance(accounttype, (int, long)), accounttype
    assert isinstance(accountid, (int, long)), accountid

    self['name'] = username
    self['account_type'] = accounttype
    self['account_id'] = accountid

    self['grimoire_score'] = self.raw_account['grimoireScore']
    self['clan'] = (self.raw_account.get('clanName') and
                    '%s [%s]' % (self.raw_account['clanName'], self.raw_account['clanTag']) or '')

    self['currency'] = {}
    for item in self.raw_account['inventory']['currencies']:
      currency = defs[item['itemHash']]
      self['currency'][currency['name'].lower().replace(' ', '_')] = item['value']

    self['characters'] = {
        long(data['characterBase']['characterId']): Character(self, data, defs=defs)
        for data in self.raw_account['characters']}

  _raw_account = None

  @property
  def raw_account(self):
    if self._raw_account is None:
      self._raw_account = self.defs.Fetch('/%(account_type)i/Account/%(account_id)i/', **self)
    return self._raw_account


class Character(dict):
  def __init__(self, user, data, defs=None):
    if defs is None:
      defs = Definitions()
    self.defs = defs

    self['account_type'] = user['account_type']
    self['account_id'] = user['account_id']
    self['character_id'] = long(data['characterBase']['characterId'])
    self['level'] = data['characterLevel']
    self['level_progress'] = (1.0 * data['levelProgression']['progressToNextLevel'] /
                              data['levelProgression']['nextLevelAt'])


if __name__ == '__main__':
  import pprint
  import sys

  for username in sys.argv[1:]:
    pprint.pprint(User(username))
