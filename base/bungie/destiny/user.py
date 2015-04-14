#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import logging
from base.bungie import platform


def Search(username, accounttype=None, bungie=None):
  if not accounttype:
    accounttype = 'all'
  if bungie is None:
    bungie = platform.Bungie()

  ret = tuple((ent['displayName'], long(ent['membershipType']), long(ent['membershipId']))
              for ent in bungie.DestinySearchDestinyPlayer(accounttype=accounttype, name=username))
  logging.info('User %s/%s has %i accounts: %r', accounttype, username, len(ret), ret)
  return ret


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None, bungie=None):
    self.bungie = bungie or platform.Bungie()

    if accounttype is None or accountid is None:
      username, accounttype, accountid = Search(username, accounttype, self.bungie)[0]

    assert isinstance(accounttype, (int, long)), accounttype
    assert isinstance(accountid, (int, long)), accountid

    self.name = username
    self.account_type = accounttype
    self.account_id = accountid

    super(User, self).__init__(
        self.bungie.DestinyAccount(accounttype=self.account_type, accountid=self.account_id)['data'])

  _characters = None

  @property
  def characters(self):
    if self._characters is None:
      self._characters = {
          long(data['characterBase']['characterId']): Character(self, data, self.bungie)
          for data in self['characters']}
    return self._characters


class Character(dict):
  def __init__(self, user, data, bungie):
    self.user = user
    self.bungie = bungie
    self.character_id = long(data['characterBase']['characterId'])
    super(Character, self).__init__(data)

  _activities = None

  @property
  def activities(self):
    if self._activities is None:
      self._activities = tuple(
          Activity(data, self.bungie) for data in self.bungie.DestinyStatsActivityHistory(
              accounttype=self.user.account_type, accountid=self.user.account_id,
              characterid=self.character_id, count=15)['data'].get('activities', ()))
    return self._activities

  _inventory = None

  @property
  def inventory(self):
    if self._inventory is None:
      self._inventory = self.bungie.DestinyAccountCharacterInventory(
          accounttype=self.user.account_type, accountid=self.user.account_id,
          characterid=self.character_id)['data']['buckets']['Equippable']
    return self._inventory

  _progress = None

  @property
  def progress(self):
    if self._progress is None:
      self._progress = self.bungie.DestinyAccountCharacterProgression(
          accounttype=self.user.account_type, accountid=self.user.account_id,
          characterid=self.character_id)['data']['progressions']
    return self._progress


class Activity(dict):
  def __init__(self, data, bungie):
    self.bungie = bungie
    self.activity_id = long(data['activityDetails']['instanceId'])
    super(Activity, self).__init__(data)

  _players = None

  @property
  def players(self):
    if self._players is None:
      self._players = tuple(self.bungie.DestinyStatsPostGameCarnageReport(
          activityid=self.activity_id)['data']['entries'])
    return self._players


if __name__ == '__main__':
  import pprint
  import sys

  for username in sys.argv[1:]:
    user = User(username)
    print '%r -> (%r, %r, %r)' % (username, user.name, user.account_type, user.account_id)
    for character_id, character in sorted(user.characters.iteritems()):
      print ' - %r: %i activities, %i items, %i progressions' % (
          character.character_id, len(character.activities), len(character.inventory),
          len(character.progress))
