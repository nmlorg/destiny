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
