#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import datetime
import logging

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
    for code, d in data.get('activities', {}).iteritems():
      self[long(code)] = {
          'name': d['activityName'].strip(),
          'desc': d['activityDescription'].strip(),
          'type': d['activityTypeHash'],
      }

    for code, d in data.get('activityTypes', {}).iteritems():
      self[long(code)] = {
          'name': d['activityTypeName'].strip(),
          'desc': d['activityTypeDescription'].strip(),
      }

    for code, d in data.get('buckets', {}).iteritems():
      self[long(code)] = {
          'name': (d.get('bucketName') or d.get('bucketIdentifier') or '').strip(),
          'desc': d.get('bucketDescription', '').strip(),
      }

    for code, d in data.get('classes', {}).iteritems():
      self[long(code)] = {
          'name': d['className'].strip(),
      }

    for code, d in data.get('genders', {}).iteritems():
      self[long(code)] = {
          'name': d['genderName'].strip(),
      }

    for code, d in data.get('items', {}).iteritems():
      self[long(code)] = {
          'name': d['itemName'].strip(),
          'desc': d.get('itemDescription', '').strip(),
          'type': d['bucketTypeHash'],
          'icon': d['icon'].strip(),
          'perks': tuple(d['perkHashes']),
      }

    for code, d in data.get('perks', {}).iteritems():
      self[long(code)] = {
          'name': d['displayName'].strip(),
          'desc': d['displayDescription'].strip(),
      }

    for code, d in data.get('races', {}).iteritems():
      self[long(code)] = {
          'name': d['raceName'].strip(),
      }

    for code, d in data.get('stats', {}).iteritems():
      self[long(code)] = {
          'name': d['statName'].strip(),
      }

    for x in data.itervalues():
      for code, d in x.iteritems():
        code = long(code)
        if code not in self:
          self[code] = {}
        self[code]['raw'] = d

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
      logging.info('Looking up %s/%s.', accounttype, username)
      data = Fetch('/SearchDestinyPlayer/%s/%s/', accounttype, username)
      assert data
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

    self['name'] = user['name']
    self['clan'] = user['clan']
    self['account_type'] = user['account_type']
    self['account_id'] = user['account_id']
    self['character_id'] = long(data['characterBase']['characterId'])
    self['level'] = data['characterLevel']
    if data.get('levelProgression'):
      self['level_progress'] = (1.0 * data['levelProgression']['progressToNextLevel'] /
                                data['levelProgression']['nextLevelAt'])
    else:
      self['level_progress'] = 0
    self['current_activity'] = None
    if defs.get(data['characterBase']['currentActivityHash']):
      current_activity = defs[data['characterBase']['currentActivityHash']]
      self['current_activity'] = {
          'name': current_activity['name'],
          'type': defs[current_activity['type']]['name'],
      }
    self['last_online'] = long(datetime.datetime.strptime(
        data['characterBase']['dateLastPlayed'], '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))
    self['class'] = defs[data['characterBase']['classHash']]['name']
    self['gender'] = defs[data['characterBase']['genderHash']]['name']
    self['race'] = defs[data['characterBase']['raceHash']]['name']
    self['emblem_banner'] = data['backgroundPath']
    self['emblem_icon'] = data['emblemPath']
    self['inventory'] = {
        defs[defs[item['itemHash']]['type']]['name'].lower().replace(' ', '_'):
            Item(self, item['itemHash'], defs=defs)
        for item in data['characterBase']['peerView']['equipment']}
    self['stats'] = {defs[v['statHash']]['name']: v['value']
                     for v in data['characterBase']['stats'].itervalues()}
    self['activities'] = tuple(Activity(self, ent, defs=defs)
                               for ent in self.raw_activities['activities'])

  _raw_activities = None

  @property
  def raw_activities(self):
    if self._raw_activities is None:
      self._raw_activities = self.defs.Fetch(
          '/Stats/ActivityHistory/%(account_type)i/%(account_id)i/%(character_id)i/'
          '?lc=en&fmt=true&lcin=true&mode=0&count=15&page=0', **self)
    return self._raw_activities

  _raw_inventory = None

  @property
  def raw_inventory(self):
    if self._raw_inventory is None:
      self._raw_inventory = defs.Fetch(
          '/%(account_type)i/Account/%(account_id)i/Character/%(character_id)i/Inventory/', **self)
    return self._raw_inventory


class Activity(dict):
  def __init__(self, character, data, defs=None):
    if defs is None:
      defs = Definitions()
    self.defs = defs

    self['name'] = defs[data['activityDetails']['referenceId']]['name']
    self['type'] = defs[defs[data['activityDetails']['referenceId']]['type']]['name']
    self['duration'] = long(data['values']['activityDurationSeconds']['basic']['value'])
    self['completed'] = bool(data['values']['completed']['basic']['value'])
    self['score'] = long(data['values']['score']['basic']['value'])


class Item(dict):
  def __init__(self, character, itemhash, defs=None):
    if defs is None:
      defs = Definitions()
    self.defs = defs

    super(Item, self).__init__(defs[itemhash])
    self['perks'] = tuple(defs[perkhash] for perkhash in self['perks'])


if __name__ == '__main__':
  import pprint
  import sys

  for username in sys.argv[1:]:
    pprint.pprint(User(username))
