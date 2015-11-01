#!/usr/bin/python

import logging


class TrackingDict(dict):
  def __init__(self, parent=None, name=None):
    self.name = name
    if isinstance(parent, TrackingDict):
      self.log = parent.log
      self.paths = {path + (name,) for path in parent.paths}
    else:
      self.log = {}
      self.paths = {()}

  def AddPath(self, basepath):
    self.paths.add(basepath)
    for key, value in self.iteritems():
      path = basepath + (key,)
      if isinstance(value, TrackingDict):
        value.AddPath(path)
      elif path not in self.log:
        self.log[path] = (value, None)
      else:
        orig = self.log[path][1]
        if orig != value:
          self.log[path] = (value, orig)
        else:
          del self.log[path]

  def __setitem__(self, key, value):
    assert value is not None
    orig = self.get(key)
    if orig == value:
      return

    super(TrackingDict, self).__setitem__(key, value)

    if not isinstance(value, dict):
      for path in self.paths:
        path += (key,)
        if path not in self.log:
          self.log[path] = (value, orig)
        else:
          orig = self.log[path][1]
          if orig != value:
            self.log[path] = (value, orig)
          else:
            del self.log[path]

  def __delitem__(self, key):
    orig = self.get(key)
    if orig is None:
      logging.error('Attempting to delete un-set key %r; ignoring.', key)
      return

    if isinstance(orig, TrackingDict):
      for path in self.paths:
        path += (key,)
        orig.paths.remove(path)

    super(TrackingDict, self).__delitem__(key)

    if not isinstance(orig, dict) or orig:
      value = None
      for path in self.paths:
        path += (key,)
        if path not in self.log:
          self.log[path] = (value, orig)
        else:
          orig = self.log[path][1]
          if orig != value:
            self.log[path] = (value, orig)
          else:
            del self.log[path]

  def __repr__(self):
    return '{%s}' % ', '.join('%r: %r' % (k, v) for k, v in sorted(self.iteritems()))


class NestedDict(TrackingDict):
  """
  >>> d = NestedDict()
  >>> d['first', 'second'] = {'third': {'fourth': [2, 4, 6]}}
  >>> sorted(d.log.iteritems())
  [(('first', 'second', 'third', 'fourth'), ([2, 4, 6], None))]
  >>> d
  {'first': {'second': {'third': {'fourth': [2, 4, 6]}}}}
  >>> d['first'] = {'second': {'third': {'fourth': [1, 3, 5]}}}
  >>> sorted(d.log.iteritems())
  [(('first', 'second', 'third', 'fourth'), ([1, 3, 5], None))]
  >>> d
  {'first': {'second': {'third': {'fourth': [1, 3, 5]}}}}
  >>> d['first', 'sixth'] = True
  >>> sorted(d.log.iteritems())
  [(('first', 'second', 'third', 'fourth'), ([1, 3, 5], None)),
   (('first', 'sixth'), (True, None))]
  >>> d
  {'first': {'second': {'third': {'fourth': [1, 3, 5]}}, 'sixth': True}}
  >>> d['first', 'seventh'] = d['first', 'second', 'third']
  >>> sorted(d.log.iteritems())
  [(('first', 'second', 'third', 'fourth'), ([1, 3, 5], None)),
   (('first', 'seventh', 'fourth'), ([1, 3, 5], None)),
   (('first', 'sixth'), (True, None))]
  >>> d
  {'first': {'second': {'third': {'fourth': [1, 3, 5]}}, 'seventh': {'fourth': [1, 3, 5]}, 'sixth': True}}
  >>> d['first', 'seventh', 'fourth'] = [3, 6, 9]
  >>> sorted(d.log.iteritems())
  [(('first', 'second', 'third', 'fourth'), ([3, 6, 9], None)),
   (('first', 'seventh', 'fourth'), ([3, 6, 9], None)),
   (('first', 'sixth'), (True, None))]
  >>> d
  {'first': {'second': {'third': {'fourth': [3, 6, 9]}}, 'seventh': {'fourth': [3, 6, 9]}, 'sixth': True}}
  >>> d['first', 'second', 'third', 'fourth'] = None

  # See TODO below.
  #>>> sorted(d.log.iteritems())
  #[(('first', 'seventh', 'fourth'), ([1, 3, 5], None)),
  # (('first', 'sixth'), (True, None))]
  #>>> d
  #{'first': {'seventh': {'fourth': [3, 6, 9]}}, 'sixth': True}}
  >>> d['first', 'seventh'] = None
  >>> sorted(d.log.iteritems())
  [(('first', 'sixth'), (True, None))]
  >>> d
  {'first': {'sixth': True}}
  """

  @staticmethod
  def NormKey(key):
    if isinstance(key, basestring):
      if key.startswith('/'):
        return key[1:].split('/')
      return key.split('.')
    return key

  def __getitem__(self, key):
    if not isinstance(key, (list, tuple)):
      rest = None
    else:
      key, rest = key[0], key[1:]

    if key:
      next = super(NestedDict, self).__getitem__(key)
    else:
      next = self

    if rest:
      return next[rest]
    return next

  def get(self, key, default=None):
    try:
      return self[key]
    except KeyError:
      return default

  def __delitem__(self, key):
    self[key] = None

  def __setitem__(self, key, value):
    if not isinstance(key, (list, tuple)):
      rest = None
    else:
      key, rest = key[0], key[1:]

    if rest:
      next = super(NestedDict, self).get(key)
      if not isinstance(next, NestedDict):
        next = NestedDict(parent=self, name=key)
        super(NestedDict, self).__setitem__(key, next)
      next[rest] = value
      # TODO: If root['a']['b'] = root['c']['d'] = next = {'x': 1}, and we execute
      # root['a']['b']['next']['x'] = None, we'll end up clearing next, root['a']['b'], and
      # root['a'], but will leave root['c']['d']['next'] as an empty dict.
      if not next:
        super(NestedDict, self).__delitem__(key)
    elif value is None:
      if not key:
        self.clear()
      elif key in self:
        super(NestedDict, self).__delitem__(key)
    elif not key:
      for k in set(self).difference(value):
        super(NestedDict, self).__delitem__(k)
      self.update(value)
    elif isinstance(value, NestedDict):
      super(NestedDict, self).__setitem__(key, value)
      for path in self.paths:
        value.AddPath(path + (key,))
    elif isinstance(value, dict):
      next = super(NestedDict, self).get(key)
      if not isinstance(next, NestedDict):
        next = NestedDict(parent=self, name=key)
        super(NestedDict, self).__setitem__(key, next)
      else:
        for k in set(next).difference(value):
          super(NestedDict, self).__delitem__(k)
      next.update(value)
    else:
      super(NestedDict, self).__setitem__(key, value)

  def update(self, values):
    if isinstance(values, dict):
      values = values.iteritems()
    for k, v in values:
      self[k] = v
