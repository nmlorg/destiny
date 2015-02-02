#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import datetime
import logging
from base.bungie import platform
from base.bungie.destiny import definitions
from base.bungie.destiny import user


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None, bungie=None, defs=None):
    if bungie is None:
      bungie = platform.Bungie()
    if defs is None:
      defs = definitions.Definitions(bungie=bungie)
    self.raw_account = account = user.User(username, accounttype, accountid, bungie=bungie)

    self['name'] = account.name
    self['account_type'] = account.account_type
    self['account_id'] = account.account_id
    self['grimoire_score'] = account['grimoireScore']
    self['clan'] = account.get('clanName', '').strip()
    if account.get('clanTag'):
      self['clan'] = ('%s [%s]' % (self['clan'], account['clanTag'])).strip()

    self['currency'] = {}
    for item in account['inventory']['currencies']:
      currency = defs[item['itemHash']]
      self['currency'][currency['name'].lower().replace(' ', '_')] = item['value']

    self['characters'] = {character_id: Character(self, character, defs)
                          for character_id, character in account.characters.iteritems()}


def ISO8601(s):
  return long(datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))


class Character(dict):
  def __init__(self, user, data, defs):
    self['name'] = user['name']
    self['clan'] = user['clan']
    self['account_type'] = user['account_type']
    self['account_id'] = user['account_id']
    self['character_id'] = data.character_id
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
    self['last_online'] = ISO8601(data['characterBase']['dateLastPlayed'])
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
    self['activities'] = tuple(Activity(ent, defs) for ent in data.activities)
    self['progress'] = {defs[ent['progressionHash']]['name']: Progression(ent)
                        for ent in data.progress}


class Activity(dict):
  def __init__(self, data, defs):
    self['name'] = defs[data['activityDetails']['referenceId']]['name']
    self['type'] = defs[defs[data['activityDetails']['referenceId']]['type']]['name']
    self['activity_id'] = long(data['activityDetails']['instanceId'])
    self['start'] = ISO8601(data['period'])
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
