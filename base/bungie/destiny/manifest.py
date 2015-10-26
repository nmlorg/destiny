#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import cPickle as pickle
import cStringIO as StringIO
import gzip
import json
import logging
import os
import pickletools
try:
  import sqlite3
except ImportError:
  sqlite3 = None
import tempfile
import zipfile
from base import bungie


def ListsToTuple(obj):
  if isinstance(obj, list):
    return tuple(ListsToTuple(x) for x in obj)
  elif isinstance(obj, dict):
    return {k: ListsToTuple(v) for k, v in obj.iteritems()}
  else:
    return obj


class Manifest(dict):
  def __init__(self):
    super(Manifest, self).__init__(bungie.GetDestinyManifest())

    definition_path = os.path.join(os.path.dirname(__file__), 'definitions.pickle.gz')
    try:
      self['definitions'] = pickle.loads(gzip.open(definition_path).read())
    except:
      self['definitions'] = {'__url__': None}

    definition_url = self['mobileWorldContentPaths']['en']
    if sqlite3 and self['definitions']['__url__'] != definition_url:
      logging.warning('Definition file %r is based on %r; fetching %r.', definition_path,
                      self['definitions']['__url__'], definition_url)
      self['definitions'] = self.FetchDefinitions(definition_url)
      self['definitions']['__url__'] = definition_url
      logging.warning('Saving %r to %r.', definition_url, definition_path + '.tmp')
      try:
        with gzip.open(definition_path + '.tmp', 'wb') as f:
          f.write(pickletools.optimize(pickle.dumps(self['definitions'], -1)))
        os.rename(definition_path + '.tmp', definition_path)
      except:
        logging.exception('Unable to update %r:', definition_path)
      else:
        logging.warning('Done.')
    del self['definitions']['__url__']

  def FetchDefinitions(self, url):
    sqldata = self.FetchData(url)
    ret = {}

    for table in sqldata.execute('select name from sqlite_master where type="table"'):
      table = table[0]
      if not table.startswith('Destiny') or not table.endswith('Definition'):
        continue
      key = table[len('Destiny'):-len('Definition')]
      ret[key] = {}
      for rowid, rowjson in sqldata.execute('select * from ' + table):
        if isinstance(rowid, (int, long)) and rowid < 0:
          rowid += 2 ** 32
        ret[key][rowid] = ListsToTuple(json.loads(rowjson))

    return ret

  def FetchContent(self, url):
    return bungie.Fetch(url)

  def FetchFile(self, url):
    return StringIO.StringIO(self.FetchContent(url))

  def FetchZip(self, url):
    return zipfile.ZipFile(self.FetchFile(url))

  def FetchData(self, url):
    zf = self.FetchZip(url)
    with tempfile.NamedTemporaryFile() as tmp:
      tmp.write(zf.open(zf.filelist[0].filename).read())
      return sqlite3.connect(tmp.name)


MANIFEST = None


def GetDef(group=None, key=None):
  global MANIFEST

  if MANIFEST is None:
    logging.warning('Loading manifest.')
    MANIFEST = Manifest()

  if group is None:
    return MANIFEST['definitions'].keys()
  if key is None:
    return MANIFEST['definitions'][group].keys()
  return MANIFEST['definitions'][group].get(key)


try:
  from google.appengine.ext import ndb
except ImportError:
  pass
else:
  class DestinyDefinition(ndb.Model):
    data = ndb.JsonProperty()

    @classmethod
    def Blank(cls):
      ndb.delete_multi(cls.query().fetch(keys_only=True))

  _GetDef = GetDef

  def GetDef(group=None, key=None):
    k = 'db:%s:%s' % (group or '-', key or '-')
    ent = DestinyDefinition.get_by_id(k)
    if ent is not None:
      return ent.data
    ret = _GetDef(group, key)
    DestinyDefinition(id=k, data=ret).put()
    return ret


if __name__ == '__main__':
  import pprint

  manifest = Manifest()

  while True:
    key = raw_input('>>> ')
    if not key:
      break
    try:
      key = long(key)
    except ValueError:
      pass
    ret = {}
    for group, codes in manifest['definitions'].iteritems():
      v = codes.get(key)
      if v is not None:
        ret[group] = v
    pprint.pprint(ret)
