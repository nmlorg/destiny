#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import logging
from base.bungie import destiny
from base.bungie.destiny import definitions


DAMAGE_TYPES = {
    0: None,
    1: 'KINETIC',
    2: 'ARC',
    3: 'SOLAR',
    4: 'VOID',
}


DEFS = None


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None):
    global DEFS

    if DEFS is None:
      DEFS = definitions.Definitions()

    if accounttype is None or accountid is None:
      for ent in destiny.SearchDestinyPlayer(username):
        logging.info('Found account %r.', ent)
        username = ent['displayName']
        accounttype = ent['membershipType']
        accountid = long(ent['membershipId'])

    assert isinstance(accounttype, (int, long)), accounttype
    assert isinstance(accountid, (int, long)), accountid

    self['name'] = username
    self['account_type'] = accounttype
    self['account_id'] = accountid

    summary = destiny.GetAccountSummary(accounttype, accountid)['data']
    all_items = destiny.GetAllItemsSummary(accounttype, accountid)['data']
    summary['inventory']['items'] = all_items['items']
    self['clan_name'] = summary.get('clanName', '').strip()
    self['clan_tag'] = summary.get('clanTag', '').strip()
    self['grimoire_score'] = summary.get('grimoireScore', 0)

    self['characters'] = []
    for ent in summary['characters']:
      character = {
          'class': DEFS[ent['characterBase']['classHash']]['name'],
          'emblem_banner': ent['backgroundPath'],
          'emblem_icon': ent['emblemPath'],
          'gender': DEFS[ent['characterBase']['genderHash']]['name'],
          'level': ent['characterLevel'],
          'light': ent['characterBase']['powerLevel'],
          'inventory': {},
          'race': DEFS[ent['characterBase']['raceHash']]['name'],
      }
      self['characters'].append(character)

    self['vault'] = {}
    for ent in summary['inventory']['items']:
      item_info = DEFS[ent['itemHash']]
      item = {
          'bound': bool(ent['transferStatus'] & 2),
          'damage_type': DAMAGE_TYPES[ent['damageType']],
          'equipped': bool(ent['transferStatus'] & 1),
          'fully_upgraded': ent['isGridComplete'],
          'icon': item_info.get('icon'),
          'id': long(ent['itemId']),
          'name': item_info['name'],
          'primary_stat_value': ent.get('primaryStat') and ent['primaryStat']['value'],
          'primary_stat_type': ent.get('primaryStat') and DEFS[ent['primaryStat']['statHash']]['name'],
          'quantity': ent['quantity'],
          'state': ent['state'],
          'type': '-',
      }
      if ent['characterIndex'] == -1:
        where = self['vault']
      else:
        where = self['characters'][ent['characterIndex']]['inventory']
      if item_info.get('type'):
        bucket = DEFS[item_info['type']]['name']
      else:
        bucket = 'Undefined (%s)' % DEFS[ent['bucketHash']]['name']
      if bucket not in where:
        where[bucket] = []
      where[bucket].append(item)
