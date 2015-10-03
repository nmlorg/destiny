#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import logging
from base.bungie import destiny
from base.bungie.destiny import manifest


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
      DEFS = manifest.Manifest()['definitions']

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
    self['account_id'] = str(accountid)

    summary = destiny.GetAccountSummary(accounttype, accountid)['data']
    all_items = destiny.GetAllItemsSummary(accounttype, accountid)['data']
    summary['inventory']['items'] = all_items['items']
    self['clan_name'] = summary.get('clanName', '').strip()
    self['clan_tag'] = summary.get('clanTag', '').strip()
    self['grimoire_score'] = summary.get('grimoireScore', 0)

    self['characters'] = []
    for ent in summary['characters']:
      character = {
          'class': GetClassName(ent['characterBase']['classHash']),
          'emblem_banner': ent['backgroundPath'],
          'emblem_icon': ent['emblemPath'],
          'gender': GetGenderName(ent['characterBase']['genderHash']),
          'level': ent['characterLevel'],
          'light': ent['characterBase']['powerLevel'],
          'inventory': {},
          'quests': {},
          'race': GetRaceName(ent['characterBase']['raceHash']),
      }
      self['characters'].append(character)

    self['vault'] = {}
    for ent in summary['inventory']['items']:
      item_info = DEFS['InventoryItem'][ent['itemHash']]

      if item_info.get('questlineItemHash'):
        quests = self['characters'][ent['characterIndex']]['quests']
        line_hash = item_info['questlineItemHash']
        line_info = DEFS['InventoryItem'][line_hash]
        quest = quests.get(line_info['itemName'])
        if quest is None:
          quest = quests[line_info['itemName']] = {
              'desc': line_info['displaySource'].strip(),
              'icon': line_info.get('icon', '/img/misc/missing_icon.png'),
              'name': line_info['itemName'],
              'steps': [],
          }
          for step_hash in line_info['setItemHashes']:
            step_info = DEFS['InventoryItem'][step_hash]
            quest['steps'].append({
                'active': False,
                'desc': step_info['displaySource'].strip(),
                'hash': step_hash,
                'name': step_info['itemName'],
                'objective': step_info['itemDescription'].strip(),
                'objectives': [GetObjective(code) for code in step_info['objectiveHashes']],
            })
        for step in quest['steps']:
          if step['hash'] == ent['itemHash']:
            step['active'] = True
        continue

      item = {
          'bound': bool(ent['transferStatus'] & 2),
          'damage_type': DAMAGE_TYPES[ent['damageType']],
          'desc': item_info.get('itemDescription', '').strip(),
          'equipped': bool(ent['transferStatus'] & 1),
          'fully_upgraded': ent['isGridComplete'],
          'hash': ent['itemHash'],
          'icon': item_info.get('icon', '/img/misc/missing_icon.png'),
          'id': long(ent['itemId']),
          'name': item_info.get('itemName', '').strip() or 'Item #%i' % ent['itemHash'],
          'primary_stat_value': ent.get('primaryStat') and ent['primaryStat']['value'],
          'primary_stat_type': (ent.get('primaryStat') and
                                GetStatName(ent['primaryStat']['statHash'])),
          'quantity': ent['quantity'],
          'state': ent['state'],
          'stats': {GetStatName(stat['statHash']): (stat['minimum'], stat['maximum'])
                    for stat in (item_info.get('stats') or {}).itervalues()},
          'tier': item_info.get('tierTypeName', '').strip(),
          'type': item_info.get('itemTypeName', '').strip(),
      }
      if ent['characterIndex'] == -1:
        where = self['vault']
      else:
        where = self['characters'][ent['characterIndex']]['inventory']
      if item_info.get('bucketTypeHash'):
        bucket = GetBucketName(item_info['bucketTypeHash'])
      else:
        bucket = 'Undefined (%s)' % GetBucketName(ent['bucketHash'])
      if bucket not in where:
        where[bucket] = []
      where[bucket].append(item)


def GetActivityName(code):
  return DEFS['Activity'][code]['activityName'].strip()


def GetBucketName(code):
  bucket = DEFS['InventoryBucket'][code]
  return (bucket.get('bucketName') or bucket.get('bucketIdentifier') or 'Bucket #%i' % code).strip()


def GetClassName(code):
  return DEFS['Class'][code]['className']


def GetDestinationName(code):
  return DEFS['Destination'][code]['destinationName'].strip()


def GetGenderName(code):
  return DEFS['Gender'][code]['genderName']


def GetObjective(code):
  objective = DEFS['Objective'][code]
  ret = {'count': objective['completionValue']}
  if objective.get('displayDescription'):
    ret['name'] = objective['displayDescription'].strip()
  elif objective.get('locationHash'):
    location = DEFS['Location'][objective['locationHash']]
    for location_release in location['locationReleases']:
      if location_release.get('activityHash'):
        ret['name'] = 'Activity: ' + GetActivityName(location_release['activityHash'])
        break
      elif location_release.get('destinationHash'):
        ret['name'] = 'Destination: ' + GetDestinationName(location_release['destinationHash'])
        break
    else:
      ret['name'] = 'Location #%i' % objective['locationHash']
  else:
    ret['name'] = 'Objective #%i' % code
  return ret


def GetRaceName(code):
  return DEFS['Race'][code]['raceName']


def GetStatName(code):
  stat = DEFS['Stat'][code]
  return (stat.get('statName') or 'Stat #%i' % code).strip()
