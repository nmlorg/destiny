#!/usr/bin/python
#
# Copyright 2015 Daniel Reed <n@ml.org>

import threading
import time
from base.bungie import bungienet
from base.net import firebase


def main():
  fb = firebase.Firebase('https://resplendent-torch-7073.firebaseio.com/')
  t = threading.Thread(target=fb.Run)
  t.daemon = True
  t.start()

  while True:
    for k in sorted(fb.state.get('users', ())):
      info = fb.state['users', k]
      if not info.get(('account', 'type')) or not info.get(('account', 'id')):
        continue
      data = bungienet.GetAccountSummary(info['account', 'type'], long(info['account', 'id']))
      characters = {}
      for character in data['data']['characters']:
        char = {
            'activity': character['characterBase']['currentActivityHash'],
            'id': character['characterBase']['characterId'],
            'stats': {
                'light': character['characterBase']['powerLevel'],
            },
        }
        characters[char['id']] = char
      if characters != info.get('characters'):
        print
        print info['account']
        print '-', info.get('characters')
        print '+', characters
        fb.Put('/users/%s/characters' % k, characters)
      time.sleep(5)


if __name__ == '__main__':
  main()
