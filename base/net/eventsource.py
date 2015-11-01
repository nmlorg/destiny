#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import logging
import socket
import time
import urllib2


class EventSource(object):
  def __init__(self, target):
    self.target = target
    self._Connect()

  running = False

  @property
  def url(self):
    return self.socket.geturl()

  def _Connect(self):
    backoff = .5

    while True:
      request = urllib2.Request(self.target, headers={'accept': 'text/event-stream'})
      try:
        self.socket = urllib2.urlopen(request)
      except:
        logging.exception('Exception while connecting to %s:', request.get_full_url())
        time.sleep(backoff)
        backoff *= 2
        if backoff > 60:
          backoff = 60
      else:
        sock = self.socket.fp._sock.fp._sock
        # Enable TCP keepalive.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Once the session becomes idle for five seconds, ...
        if hasattr(socket, 'TCP_KEEPIDLE'):
          sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
        elif hasattr(socket, 'TCP_KEEPALIVE'):
          sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, 10)
        # ... send a ping every 5 seconds.
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
        # Break the connection after 2 failures.
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
        handler = getattr(self, 'onconnect', None)
        if handler:
          handler()
        break

  def _ReadLine(self):
    ret = []
    while True:
      try:
        c = self.socket.read(1)
      except:
        return
      if c:
        ret.append(c)
      if not c or c == '\n':
        return ''.join(ret)

  def Run(self):
    self.running = True
    data = []
    event = 'message'
    while self.running:
      line = self._ReadLine()
      if not line:
        logging.error('Reconnecting to %s.', self.target)
        self._Connect()
        data = []
        event = 'message'
        continue
      line = line.strip()
      if not line:
        handler = getattr(self, 'on' + event.replace('-', '_'), None)
        if handler:
          handler('\n'.join(data))
        data = []
        event = 'message'
      elif line.startswith('data:'):
        data.append(line[len('data:'):].strip())
      elif line.startswith('event:'):
        event = line[len('event:'):].strip()
