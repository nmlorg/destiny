#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

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


class User(dict):
  def __init__(self, username, accounttype=None, accountid=None):
    if accounttype is None or accountid is None:
      if not accounttype:
        accounttype = 'All'
      data = Fetch('/SearchDestinyPlayer/%s/%s/', accounttype, username)
      assert data and len(data) == 1, data
      username = data[0]['displayName']
      accounttype = long(data[0]['membershipType'])
      accountid = long(data[0]['membershipId'])

    assert isinstance(accounttype, (int, long)), accounttype
    assert isinstance(accountid, (int, long)), accountid

    self['name'] = username
    self['account_type'] = accounttype
    self['account_id'] = accountid


if __name__ == '__main__':
  import pprint
  import sys

  for username in sys.argv[1:]:
    pprint.pprint(User(username))
