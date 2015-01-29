#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import datetime
import logging
from base.bungie import definitions
from base.bungie import platform


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None, bungie=None, defs=None):
    self.bungie = bungie or platform.Bungie()
    self.defs = defs or definitions.Definitions(bungie=bungie)

    if accounttype is None or accountid is None:
      if not accounttype:
        accounttype = 'All'
      logging.info('Looking up %s/%s.', accounttype, username)
      data = self.bungie.Fetch('destiny/SearchDestinyPlayer/%s/%s/', accounttype, username)
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
    self['clan'] = (
        self.raw_account.get('clanName') and
        '%s [%s]' % (self.raw_account['clanName'], self.raw_account.get('clanTag', '')) or '')

    self['currency'] = {}
    for item in self.raw_account['inventory']['currencies']:
      currency = self.defs[item['itemHash']]
      self['currency'][currency['name'].lower().replace(' ', '_')] = item['value']

    self['characters'] = {
        long(data['characterBase']['characterId']): Character(self, data, self.bungie, self.defs)
        for data in self.raw_account['characters']}

  _raw_account = None

  @property
  def raw_account(self):
    if self._raw_account is None:
      self._raw_account = self.bungie.Fetch('destiny/%(account_type)i/Account/%(account_id)i/', **self)['data']
    return self._raw_account


class Character(dict):
  def __init__(self, user, data, bungie, defs):
    self.bungie = bungie

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
            Item(item['itemHash'], defs)
        for item in data['characterBase']['peerView']['equipment']}
    self['stats'] = {defs[v['statHash']]['name']: v['value']
                     for v in data['characterBase']['stats'].itervalues()}
    self['activities'] = tuple(Activity(ent, defs)
                               for ent in self.raw_activities['activities'])
    self['progress'] = {defs[ent['progressionHash']]['name']: Progression(ent)
                        for ent in self.raw_progress['progressions']}

  _raw_activities = None

  @property
  def raw_activities(self):
    if self._raw_activities is None:
      self._raw_activities = self.bungie.Fetch(
          'destiny/Stats/ActivityHistory/%(account_type)i/%(account_id)i/%(character_id)i/'
          '?lc=en&fmt=true&lcin=true&mode=0&count=15&page=0', **self)['data']
    return self._raw_activities

  _raw_inventory = None

  @property
  def raw_inventory(self):
    if self._raw_inventory is None:
      self._raw_inventory = self.bungie.Fetch(
          'destiny/%(account_type)i/Account/%(account_id)i/Character/%(character_id)i/Inventory/',
          **self)['data']
    return self._raw_inventory

  _raw_progress = None

  @property
  def raw_progress(self):
    if self._raw_progress is None:
      self._raw_progress = self.bungie.Fetch(
          'destiny/%(account_type)i/Account/%(account_id)i/Character/%(character_id)i/Progression/',
          **self)['data']
    return self._raw_progress


class Activity(dict):
  def __init__(self, data, defs):
    self['name'] = defs[data['activityDetails']['referenceId']]['name']
    self['type'] = defs[defs[data['activityDetails']['referenceId']]['type']]['name']
    self['duration'] = long(data['values']['activityDurationSeconds']['basic']['value'])
    self['completed'] = bool(data['values']['completed']['basic']['value'])
    self['score'] = long(data['values']['score']['basic']['value'])


class Item(dict):
  def __init__(self, itemhash, defs):
    super(Item, self).__init__(defs[itemhash])
    self['perks'] = tuple(defs[perkhash] for perkhash in self['perks'])


class Progression(dict):
  def __init__(self, data):
    self['level'] = data['level']
    self['current'] = data['progressToNextLevel']
    self['next'] = data['nextLevelAt']
    self['daily'] = data['dailyProgress']
    self['weekly'] = data['weeklyProgress']


if __name__ == '__main__':
  import pprint
  import sys

  for username in sys.argv[1:]:
    pprint.pprint(User(username))
