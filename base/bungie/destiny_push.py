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


def main():
  os.environ['TZ'] = 'UTC'
  time.tzset()

  fb = firebase.Firebase('https://resplendent-torch-7073.firebaseio.com/')
  t = threading.Thread(target=fb.Run)
  t.daemon = True
  t.start()

  while True:
    for player_name in sorted(fb.state.get('players', ())):
      player_info = fb.state['players', player_name]
      if not isinstance(player_info, dict):
        player_info = nested_dict.NestedDict()
      if player_info.get('last_search', 0) < time.time() - 60 * 60 * 5:
        print
        print 'Searching for accounts under the name %r.' % player_name
        current_accounts = set(player_info.get('accounts', ()))
        for res in bungienet.SearchDestinyPlayer(player_name):
          if res['membershipId'] in current_accounts:
            current_accounts.remove(res['membershipId'])
          player_info['accounts', res['membershipId'], 'id'] = res['membershipId']
          player_info['accounts', res['membershipId'], 'type'] = res['membershipType']
          player_info['accounts', res['membershipId'], 'name'] = res['displayName']
        for account_id in current_accounts:
          del player['accounts', account_id]
        player_info['last_search'] = time.time()
        fb.Put(('players', player_name), player_info)
        print

      for account_id in sorted(player_info.get('accounts', ())):
        account_info = player_info['accounts', account_id]
        if not account_info.get('type') or not account_info.get('id'):
          continue
        raw_data = bungienet.GetAccountSummary(account_info['type'],
                                               long(account_info['id']))['data']

        characters = {}
        for i, raw_char in enumerate(raw_data['characters']):
          last_online = manifest.ISO8601(raw_char['characterBase']['dateLastPlayed'])
          if last_online >= time.time() - 60:
            last_online = 0
          char = {
              'active': not i,
              'attrs': {
                  'class': manifest.GetClassName(raw_char['characterBase']['classHash']),
                  'gender': manifest.GetGenderName(raw_char['characterBase']['genderHash']),
                  'race': manifest.GetRaceName(raw_char['characterBase']['raceHash']),
              },
              'id': raw_char['characterBase']['characterId'],
              'last_online': last_online,
              'stats': {
                  'level': raw_char['characterLevel'],
              },
          }
          for stat in raw_char['characterBase']['stats'].itervalues():
            char['stats'][manifest.GetStatName(stat['statHash']).lower()] = stat['value']
          characters[char['id']] = char
        if characters != account_info.get('characters'):
          fb.Put(('players', player_name, 'accounts', account_id, 'characters'), characters)

        current_char_id = raw_data['characters'][0]['characterBase']['characterId']
        activity_code = raw_data['characters'][0]['characterBase']['currentActivityHash']
        activity = {
            'code': activity_code,
            'end': characters[current_char_id]['last_online'],
            'name': manifest.GetActivityName(activity_code),
        }
        if activity != account_info.get('activity'):
          fb.Put(('players', player_name, 'accounts', account_id, 'activity'), activity)

        time.sleep(2)


if __name__ == '__main__':
  main()
