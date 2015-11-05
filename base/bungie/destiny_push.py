#!/usr/bin/python
#
# Copyright 2015 Daniel Reed <n@ml.org>

import os
import threading
import time
from base.bungie import bungienet
from base.bungie import manifest
from base.net import firebase
from base.util import nested_dict


ACCOUNT_TYPES = {
    1: 'XBL',
    2: 'PSN',
}
ACCOUNT_TYPE_NAMES = {v: k for k, v in ACCOUNT_TYPES.iteritems()}


def main():
  os.environ['TZ'] = 'UTC'
  time.tzset()

  fb = firebase.Firebase('https://resplendent-torch-7073.firebaseio.com/')
  t = threading.Thread(target=fb.Run)
  t.daemon = True
  t.start()

  def SetIf(key, val):
    if fb.state.get(key) != val:
      fb.Put(key, val)

  while True:
    for player_name in sorted(fb.state.get('players', ())):
      player_info = fb.state.get(('players', player_name))
      if player_info is None:
        continue
      if (not isinstance(player_info, dict) or
          player_info.get('last_search', 0) < time.time() - 60 * 60 * 5):
        print
        print 'Searching for accounts under the name %r.' % player_name
        accounts = {}
        for res in bungienet.SearchDestinyPlayer(player_name):
          account_type = (ACCOUNT_TYPES.get(res['membershipType']) or
                          'Network #%i' % res['membershipType'])
          accounts[account_type] = res['membershipId']
          SetIf(('accounts', res['membershipId'], 'name'), res['displayName'])
          SetIf(('accounts', res['membershipId'], 'player'), player_name)
          SetIf(('accounts', res['membershipId'], 'type'), res['membershipType'])
        SetIf(('players', player_name), {'accounts': accounts, 'last_search': time.time()})
        print
        time.sleep(2)

    for account_id in sorted(fb.state.get('accounts', ())):
      account_info = fb.state.get(('accounts', account_id))
      if account_info is None:
        continue
      player_info = fb.state.get(('players', account_info['player']))
      if player_info is None or account_id not in (player_info.get('accounts') or {}).values():
        print
        print "Account %r's player, %r, is no longer tracked (or no longer owns it); deleting." % (
            account_id, account_info['player'])
        SetIf(('accounts', account_id), None)
        print
        continue
      raw_data = bungienet.GetAccountSummary(account_info['type'], long(account_id))['data']
      characters = set()
      for i, raw_char in enumerate(raw_data['characters']):
        raw_base = raw_char['characterBase']
        characters.add(raw_base['characterId'])
        last_online = manifest.ISO8601(raw_base['dateLastPlayed'])
        if last_online >= time.time() - 60:
          last_online = 0
        activity_code = raw_base['currentActivityHash']
        char = {
            'account': account_id,
            'active': not i,
            'activity': {
                'code': activity_code,
                'end': last_online,
                'name': manifest.GetActivityName(activity_code),
            },
            'attrs': {
                'class': manifest.GetClassName(raw_base['classHash']),
                'gender': manifest.GetGenderName(raw_base['genderHash']),
                'race': manifest.GetRaceName(raw_base['raceHash']),
            },
            'stats': {
                'level': raw_char['characterLevel'],
            },
        }
        for stat in raw_base['stats'].itervalues():
          char['stats'][manifest.GetStatName(stat['statHash']).lower()] = stat['value']
        if fb.state.get(('characters', raw_base['characterId'])) != char:
          SetIf(('characters', raw_base['characterId']), char)

      characters = sorted(characters)
      if characters != account_info.get('characters'):
        SetIf(('accounts', account_id, 'characters'), characters)

      time.sleep(2)

    for char_id in sorted(fb.state.get('characters', ())):
      char_info = fb.state.get(('characters', char_id))
      if char_info is None:
        continue
      account_info = fb.state.get(('accounts', char_info['account']))
      if account_info is None or char_id not in account_info.get('characters', ()):
        print
        print "Character %r's account, %r, is no longer tracked (or no longer owns it); deleting." % (
            char_id, char_info['account'])
        SetIf(('characters', char_id), None)
        print


if __name__ == '__main__':
  main()
