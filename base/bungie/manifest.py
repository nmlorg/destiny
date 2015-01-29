#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import cPickle as pickle
import cStringIO as StringIO
import gzip
import json
import logging
import os
try:
  import sqlite3
except ImportError:
  sqlite3 = None
import tempfile
import zipfile
from base.bungie import platform


def ListsToTuple(obj):
  if isinstance(obj, list):
    return tuple(ListsToTuple(x) for x in obj)
  elif isinstance(obj, dict):
    return {k: ListsToTuple(v) for k, v in obj.iteritems()}
  else:
    return obj


class Manifest(dict):
  def __init__(self, bungie=None):
    self.bungie = bungie or platform.Bungie()
    super(Manifest, self).__init__(self.bungie.DestinyManifest())

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
        pickle.dump(self['definitions'], gzip.open(definition_path + '.tmp', 'wb'), -1)
        logging.warning('Done.')
        os.rename(definition_path + '.tmp', definition_path)
      except:
        logging.exception('Unable to update %r:', definition_path)

  def FetchDefinitions(self, url):
    sqldata = self.FetchData(url)
    ret = {}

    for table in ('ActivityBundle', 'Activity', 'ActivityType', 'Class', 'Destination',
                  'DirectorBook', 'Faction', 'Gender', 'GrimoireCard', 'Grimoire',
                  'InventoryBucket', 'InventoryItem', 'Place', 'Progression', 'Race', 'SandboxPerk',
                  'SpecialEvent', 'Stat', 'StatGroup', 'TalentGrid', 'UnlockFlag', 'Vendor'):
      ret[table] = {}
      for rowid, rowjson in sqldata.execute('select id, json from Destiny%sDefinition' % (table,)):
        if rowid < 0:
          rowid += 2 ** 32
        ret[table][rowid] = ListsToTuple(json.loads(rowjson))

    for table in ('HistoricalStats',):
      ret[table] = {
          k: ListsToTuple(json.loads(v))
          for k, v in sqldata.execute('select key, json from Destiny%sDefinition' % (table,))}

    return ret

  def FetchContent(self, url):
    return self.bungie.Fetch(url)

  def FetchFile(self, url):
    return StringIO.StringIO(self.FetchContent(url))

  def FetchZip(self, url):
    return zipfile.ZipFile(self.FetchFile(url))

  def FetchData(self, url):
    zf = self.FetchZip(url)
    with tempfile.NamedTemporaryFile() as tmp:
      tmp.write(zf.open(zf.filelist[0].filename).read())
      return sqlite3.connect(tmp.name)


if __name__ == '__main__':
  manifest = Manifest()

  for k, v in sorted(manifest['definitions'].iteritems()):
    if k != '__url__':
      print '%s: %i definitions.' % (k, len(v))
