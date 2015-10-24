#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import datetime
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


def GetDestinyUser(username, accounttype=None, accountid=None):
  if accounttype is None or accountid is None:
    for ent in destiny.SearchDestinyPlayer(username):
      username = ent['displayName']
      accounttype = ent['membershipType']
      accountid = long(ent['membershipId'])
      break

  assert isinstance(accounttype, (int, long)), accounttype
  assert isinstance(accountid, (int, long)), accountid

  summary = destiny.GetAccountSummary(accounttype, accountid)['data']
  all_items = destiny.GetAllItemsSummary(accounttype, accountid)['data']
  summary['inventory']['items'] = all_items['items']

  for ent in summary['characters']:
    charid = long(ent['characterBase']['characterId'])
    advisors = destiny.GetAdvisorsForCurrentCharacter(accounttype, charid)
    ent['advisors'] = (
        advisors and advisors['data'] or {'activityAdvisors': {}, 'vendorAdvisors': {}})
    ent['history'] = destiny.GetActivityHistory(
        accounttype, accountid, charid, 'None', count=20)['data']['activities']
    for history in ent['history']:
      for k, v in destiny.GetPostGameCarnageReport(
          history['activityDetails']['instanceId'])['data'].iteritems():
        history[k] = v
    ent['progressions'] = destiny.GetCharacterProgression(
        accounttype, accountid, charid)['data']['progressions']

  charids = [long(ent['characterBase']['characterId']) for ent in summary['characters']]
  for ent in summary['inventory']['items']:
    if long(ent.get('itemId', 0)):
      charid = charids[ent['characterIndex']]
      ent['details'] = destiny.GetItemDetail(accounttype, accountid, charid, ent['itemId'])['data']

  return username, accounttype, accountid, summary


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None):
    username, accounttype, accountid, summary = GetDestinyUser(username, accounttype, accountid)

    self['name'] = username
    self['account_type'] = accounttype
    self['account_id'] = str(accountid)
    self['clan_name'] = summary.get('clanName', '').strip()
    self['clan_tag'] = summary.get('clanTag', '').strip()
    self['grimoire_score'] = summary.get('grimoireScore', 0)
    self['characters'] = []
    for ent in summary['characters']:
      bounties = []
      for vendor in ent['advisors']['vendorAdvisors'].itervalues():
        if not vendor.get('pendingBounties'):
          continue
        for bounty in vendor['pendingBounties']['saleItems']:
          item_info = manifest.GetDef('InventoryItem', bounty['item']['itemHash'])
          bounties.append({
              'active': False,
              'desc': item_info.get('itemDescription', '').strip(),
              'hash': bounty['item']['itemHash'],
              'icon': item_info.get('icon', '/img/misc/missing_icon.png'),
              'name': item_info.get('itemName', '').strip() or 'Item #%i' % ent['itemHash'],
              'objectives': [GetObjective(code) for code in item_info['objectiveHashes']],
              'rewards': [GetReward(long(code)) for code in item_info['values']],
              'sources': [GetSource(code) for code in item_info.get('sourceHashes', ())],
          })

      self['characters'].append({
          'activities': GetActivityCompletion(ent['advisors']),
          'bounties': bounties,
          'class': GetClassName(ent['characterBase']['classHash']),
          'emblem_banner': ent['backgroundPath'],
          'emblem_icon': ent['emblemPath'],
          'gender': GetGenderName(ent['characterBase']['genderHash']),
          'history': [GetHistoryActivity(activity) for activity in ent['history']],
          'id': ent['characterBase']['characterId'],
          'level': ent['characterLevel'],
          'light': ent['characterBase']['powerLevel'],
          'inventory': {},
          'progress': dict(GetProgression(prog) for prog in ent['progressions']),
          'quests': {},
          'race': GetRaceName(ent['characterBase']['raceHash']),
          'stats': {GetStatName(stat['statHash']): stat['value']
                    for stat in ent['characterBase']['stats'].itervalues()},
      })

    self['vault'] = {}
    for ent in summary['inventory']['items']:
      item_info = manifest.GetDef('InventoryItem', ent['itemHash']) or {}
      if item_info.get('bucketTypeHash'):
        bucket_name = GetBucketName(item_info['bucketTypeHash'])
      else:
        bucket_name = 'Undefined (%s)' % GetBucketName(ent['bucketHash'])

      if item_info.get('questlineItemHash'):
        quests = self['characters'][ent['characterIndex']]['quests']
        line_hash = item_info['questlineItemHash']
        line_info = manifest.GetDef('InventoryItem', line_hash)
        quest = quests.get(line_info['itemName'])
        if quest is None:
          quest = quests[line_info['itemName']] = {
              'desc': line_info['displaySource'].strip(),
              'hash': line_hash,
              'icon': line_info.get('icon', '/img/misc/missing_icon.png'),
              'name': line_info['itemName'],
              'steps': [],
          }
          for step_hash in line_info['setItemHashes']:
            step_info = manifest.GetDef('InventoryItem', step_hash)
            quest['steps'].append({
                'active': False,
                'desc': step_info['displaySource'].strip(),
                'hash': step_hash,
                'name': step_info['itemName'],
                'objective': step_info['itemDescription'].strip(),
                'objectives': [GetObjective(code) for code in step_info['objectiveHashes']],
                'rewards': [GetReward(long(code)) for code in step_info['values']],
            })
        for step in quest['steps']:
          if step['hash'] == ent['itemHash']:
            step['active'] = True
        continue

      if bucket_name == 'Bounties':
        bounties = self['characters'][ent['characterIndex']]['bounties']
        bounty = {
            'active': True,
            'desc': item_info.get('itemDescription', '').strip(),
            'hash': ent['itemHash'],
            'icon': item_info.get('icon', '/img/misc/missing_icon.png'),
            'name': item_info.get('itemName', '').strip() or 'Item #%i' % ent['itemHash'],
            'objectives': [GetObjective(code) for code in item_info['objectiveHashes']],
            'rewards': [GetReward(long(code)) for code in item_info['values']],
            'sources': [GetSource(code) for code in item_info.get('sourceHashes', ())],
        }
        for i, currentBounty in enumerate(bounties):
          if currentBounty['hash'] == bounty['hash']:
            bounties[i] = bounty
            break
        else:
          bounties.append(bounty)
        continue

      if ent.get('details'):
        perks = [GetPerk(perk['perkHash']) for perk in ent['details']['item']['perks']]
      else:
        perks = []
      item = {
          'class': GetClassFromCategories(item_info.get('itemCategoryHashes', ())),
          'damage_type': DAMAGE_TYPES[ent['damageType']],
          'desc': item_info.get('itemDescription', '').strip(),
          'equipped': bool(ent['transferStatus'] & 1),
          'fully_upgraded': ent['isGridComplete'],
          'hash': ent['itemHash'],
          'icon': item_info.get('icon', '/img/misc/missing_icon.png'),
          'id': ent['itemId'],
          'name': item_info.get('itemName', '').strip() or 'Item #%i' % ent['itemHash'],
          'objectives': [GetObjective(code) for code in item_info.get('objectiveHashes', ())],
          'perks': perks,
          'primary_stat_value': ent.get('primaryStat') and ent['primaryStat']['value'],
          'primary_stat_type': (ent.get('primaryStat') and
                                GetStatName(ent['primaryStat']['statHash'])),
          'quantity': ent['quantity'],
          'sources': [GetSource(code) for code in item_info.get('sourceHashes', ())],
          'state': ent['state'],
          'tier': item_info.get('tierTypeName', '').strip(),
          'transferrable': not item_info.get('nonTransferrable', True),
          'type': item_info.get('itemTypeName', '').strip(),
      }
      if ent['characterIndex'] == -1:
        where = self['vault']
      else:
        where = self['characters'][ent['characterIndex']]['inventory']
      if bucket_name not in where:
        where[bucket_name] = []
      where[bucket_name].append(item)


def GetActivity(code):
  return manifest.GetDef('Activity', code)


RAID_STEPS = {
    'RAID_MOON1': (
        'Traverse the Abyss',
        'Cross the Bridge',
        u'Ir Y\xfbt, the Deathsinger',
        'Crota',
    ),
    'RAID_TAKEN_KING': (
        'Power the Glyph (Basilica)',
        'Defeat the Warpriest (Basilica)',
        "Defeat Golgoroth (Golgoroth's Cellar)",
        'Defeat the Daughters of Oryx (Threshold)',
        'Defeat Oryx, the Taken King (Threshold)',
    ),
    'RAID_VENUS1': (
        "Destroy the Oracles (Templar's Well)",
        "Defeat the Templar (Templar's Well)",
        'Awaken the Glass Throne (Vault of Glass)',
        'Destroy Atheon (Vault of Glass)',
    ),
}


def GetActivityCompletion(advisors):
  activities = []
  for ent in advisors.get('weeklyCrucible', ()):
    bundle = manifest.GetDef('ActivityBundle', ent['activityBundleHash'])
    for code in bundle['activityHashes']:
      activity = GetActivity(code)
      activities.append({
          'complete': ent['isCompleted'],
          'desc': activity['activityDescription'],
          'hash': code,
          'icon': ent['iconPath'],
          'modifiers': [],
          'name': activity['activityName'].strip(),
          'period': 'Weekly',
          'rewards': GetActivityRewards(activity),
          'steps': [{'complete': ent['isCompleted'],
                     'name': 'Completed'}],
          'type': 'Crucible',
      })
  for ent in advisors['activityAdvisors'].itervalues():
    if ent.get('dailyChapterActivities'):
      for code in ent['dailyChapterActivities']['tierActivityHashes']:
        activity = GetActivity(code)
        activities.append({
            'complete': ent['dailyChapterActivities']['isCompleted'],
            'desc': activity['activityDescription'],
            'hash': code,
            'icon': activity['releaseIcon'],
            'modifiers': [GetModifier(skull) for skull in activity['skulls']],
            'name': '%s (%i)' % (activity['activityName'].strip(), activity['activityLevel']),
            'period': 'Daily',
            'rewards': GetActivityRewards(activity),
            'steps': [{'complete': ent['dailyChapterActivities']['isCompleted'],
                       'name': 'Completed'}],
            'type': 'Mission',
        })
    elif ent.get('dailyCrucible'):
      bundle = manifest.GetDef('ActivityBundle', ent['activityBundleHash'])
      for code in bundle['activityHashes']:
        activity = GetActivity(code)
        activities.append({
            'complete': ent['dailyCrucible']['isCompleted'],
            'desc': activity['activityDescription'],
            'hash': code,
            'icon': ent['dailyCrucible']['iconPath'],
            'modifiers': [],
            'name': activity['activityName'].strip(),
            'period': 'Daily',
            'rewards': GetActivityRewards(activity),
            'steps': [{'complete': ent['dailyCrucible']['isCompleted'],
                       'name': 'Completed'}],
            'type': 'Crucible',
        })
    elif ent.get('raidActivities'):
      bundle = manifest.GetDef('ActivityBundle', ent['activityBundleHash'])
      step_names = RAID_STEPS.get(ent['raidActivities']['raidIdentifier'])
      for tier in ent['raidActivities']['tiers']:
        activity = GetActivity(tier['activityHash'])
        activities.append({
            'complete': tier['stepsComplete'] == tier['stepsTotal'],
            'desc': activity['activityDescription'],
            'hash': tier['activityHash'],
            'icon': bundle['releaseIcon'],
            'modifiers': [GetModifier(skull) for skull in activity['skulls']],
            'name': '%s (%i)' % (activity['activityName'].strip(), activity['activityLevel']),
            'period': 'Weekly',
            'rewards': GetActivityRewards(activity),
            'steps': [{'complete': step['isComplete'],
                       'name': step_names and step_names[i] or 'Step #%i' % (i + 1)}
                      for i, step in enumerate(tier['steps'])],
            'type': 'Raid',
        })
  return activities


def GetActivityName(code):
  return GetActivity(code)['activityName'].strip()


def GetActivityRewards(activity):
  rewards = []
  for reward_set in activity['rewards']:
    for reward in reward_set['rewardItems']:
      rewards.append(GetReward(reward['itemHash']))
  return rewards


def GetBucketName(code):
  bucket = manifest.GetDef('InventoryBucket', code)
  return (bucket.get('bucketName') or bucket.get('bucketIdentifier') or 'Bucket #%i' % code).strip()


def GetClassFromCategories(codes):
  for code in codes:
    category = manifest.GetDef('ItemCategory', code)
    if category['identifier'].startswith('CATEGORY_CLASS_'):
      return category['title'].strip()


def GetClassName(code):
  return manifest.GetDef('Class', code)['className']


def GetDestinationName(code):
  return manifest.GetDef('Destination', code)['destinationName'].strip()


def GetGenderName(code):
  return manifest.GetDef('Gender', code)['genderName']


def GetHistoryActivity(activity):
  players = []
  for ent in activity['entries']:
    bungie_info = ent['player'].get('bungieNetUserInfo')
    destiny_info = ent['player']['destinyUserInfo']
    players.append({
        'icon': bungie_info and bungie_info['iconPath'] or destiny_info['iconPath'],
        'name': destiny_info['displayName'],
    })
  players.sort(key=lambda ent: ent['name'])

  start = ISO8601(activity['period'])
  return {
      'complete': bool(activity['values']['completed']['basic']['value']),
      'duration': activity['values']['activityDurationSeconds']['basic']['displayValue'],
      'end': start + activity['values']['activityDurationSeconds']['basic']['value'],
      'name': GetActivityName(activity['activityDetails']['referenceId']),
      'players': players,
      'start': start,
  }


def GetModifier(data):
  return {
      'desc': data['description'],
      'icon': data['icon'],
      'name': data['displayName'],
  }


def GetObjective(code):
  objective = manifest.GetDef('Objective', code)
  ret = {'count': objective['completionValue']}
  if objective.get('displayDescription'):
    ret['name'] = objective['displayDescription'].strip()
  elif objective.get('locationHash'):
    location = manifest.GetDef('Location', objective['locationHash'])
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


def GetPerk(code):
  perk = manifest.GetDef('SandboxPerk', code)
  return {
      'desc': perk.get('displayDescription', 'Undefined perk').strip(),
      'hidden': not perk['isDisplayable'],
      'icon': perk['displayIcon'],
      'name': perk.get('displayName') or '#%i' % code,
  }


def GetProgression(progression):
  info = manifest.GetDef('Progression', progression['progressionHash'])
  return info['name'], {
      'current': progression['progressToNextLevel'],
      'daily': progression['dailyProgress'],
      'icon': info.get('icon', '/img/misc/missing_icon.png'),
      'level': progression['level'],
      'levels': 0 if info['repeatLastStep'] else len(info['steps']),
      'next': progression['nextLevelAt'],
      'total': progression['currentProgress'],
      'weekly': progression['weeklyProgress'],
  }


def GetRaceName(code):
  return manifest.GetDef('Race', code)['raceName']


def GetReward(code):
  reward = manifest.GetDef('InventoryItem', code) or {}
  return {
      'icon': reward.get('icon', '/img/misc/missing_icon.png'),
      'name': reward.get('itemName') or 'Reward #%i' % code,
  }


def GetSource(code):
  source = manifest.GetDef('RewardSource', code) or {}
  return {
      'desc': source.get('description', ''),
      'icon': source.get('icon', '/img/misc/missing_icon.png'),
      'name': source.get('sourceName') or 'Source #%i' % code,
  }


def GetStatName(code):
  stat = manifest.GetDef('Stat', code)
  return (stat.get('statName') or 'Stat #%i' % code).strip()


def ISO8601(s):
  return long(datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))
