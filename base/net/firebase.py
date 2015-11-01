#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import json
import logging
import re
import time
import urllib2
from base.net import eventsource
from base.util import nested_dict


class Firebase(object):
  def __init__(self, url, onupdate=None, pushonreconnect=False):
    self._url_prefix, self._url_path, self._url_params = re.match(
        '^([a-z]*:[/][/][^/]*)([/]?[^?]*)([?]?.*)$', url).groups()
    self._url_suffix = self._url_prefix.endswith('firebaseio.com') and '.json' or ''
    url = '%s%s%s%s' % (self._url_prefix, self._url_path, self._url_suffix, self._url_params)
    self.state = nested_dict.NestedDict()
    if onupdate:
      self.onupdate = onupdate
    self._eventsource = eventsource.EventSource(url)
    if pushonreconnect:
      self._eventsource.onconnect = self._HandleReconnect
    self._eventsource.onput = self._HandlePut
    self._eventsource.onpatch = self._HandlePatch

  def Run(self):
    self._eventsource.Run()

  def onupdate(self, log):
    for k, (v, prev) in sorted(log.iteritems()):
      logging.error('%s: %r -> %r', '.'.join(k), prev, v)

  def _HandleReconnect(self):
    logging.error('Reconnected; uploading current state.')
    self.Put('', self.state)

  def _HandlePut(self, data):
    data = json.loads(data)
    key = self.state.NormKey(data['path'])
    if key:
      self.state[key] = data['data']
    else:
      self.state.clear()
      if isinstance(data['data'], dict):
        self.state.update(data['data'])
    if self.state.log:
      self.onupdate(self.state.log)
      self.state.log.clear()

  def _HandlePatch(self, data):
    data = json.loads(data)
    key = self.state.NormKey(data['path'])
    if key:
      container = self.state[key]
    else:
      container = self.state
    for k, v in data['data'].iteritems():
      container[k] = v
    if self.state.log:
      self.onupdate(self.state.log)
      self.state.log.clear()

  def Put(self, path, value):
    if not path.startswith('/'):
      path = '%s/%s' % (self._url_path, path)
    return Put('%s%s%s%s' % (self._url_prefix, path, self._url_suffix, self._url_params), value)


def Put(url, value):
  backoff = .5

  while True:
    req = urllib2.Request(url, data=json.dumps(value))
    req.add_header('Content-Type', 'application/json')
    req.get_method = lambda: 'PUT'
    try:
      return json.loads(urllib2.urlopen(req).read())
    except:
      logging.exception('Exception while connecting to %s:', req.get_full_url())
      time.sleep(backoff)
      backoff *= 2
      if backoff > 10:
        backoff = 10


if __name__ == '__main__':
  import sys
  import threading

  for url in sys.argv[1:]:
    threading.Thread(target=Firebase(url).Run).start()
