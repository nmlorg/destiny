#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

import cStringIO as StringIO
import json
import sqlite3
import tempfile
import zipfile
from base.bungie import platform


class Manifest(dict):
  def __init__(self):
    self.bungie = platform.Bungie()
    manifest = self.bungie.Fetch('destiny/manifest/')
    self['version'] = manifest['version']

    sqldata = self.FetchData(manifest['mobileWorldContentPaths']['en'])

    for table in ('ActivityBundle', 'Activity', 'ActivityType', 'Class', 'Destination',
                  'DirectorBook', 'Faction', 'Gender', 'GrimoireCard', 'Grimoire',
                  'InventoryBucket', 'InventoryItem', 'Place', 'Progression', 'Race', 'SandboxPerk',
                  'SpecialEvent', 'Stat', 'StatGroup', 'TalentGrid', 'UnlockFlag', 'Vendor'):
      self[table] = {}
      for rowid, rowjson in sqldata.execute('select id, json from Destiny%sDefinition' % (table,)):
        if rowid < 0:
          rowid += 2 ** 32
        self[table][rowid] = json.loads(rowjson)

    for table in ('HistoricalStats',):
      self[table] = {
          k: json.loads(v)
          for k, v in sqldata.execute('select key, json from Destiny%sDefinition' % (table,))}

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
  import pprint

  pprint.pprint(Manifest())
