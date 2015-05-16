#!/usr/bin/python
#
# Copyright 2014 Daniel Reed <n@ml.org>

from base.bungie.destiny import manifest


class Definitions(dict):
  def __init__(self, definitions=None, bungie=None):
    if definitions is None:
      definitions = manifest.Manifest(bungie=bungie)['definitions']

    for code, d in definitions['Activity'].iteritems():
      self[code] = {
          'name': d.get('activityName', '').strip() or 'Activity #%i' % code,
          'desc': d.get('activityDescription', '').strip(),
          'type': d['activityTypeHash'],
      }

    for code, d in definitions['ActivityType'].iteritems():
      self[code] = {
          'name': (d.get('activityTypeName') or d['identifier']).strip(),
          'desc': d.get('activityTypeDescription', '').strip(),
      }

    for code, d in definitions['InventoryBucket'].iteritems():
      self[code] = {
          'name': (d.get('bucketName') or d.get('bucketIdentifier') or '').strip(),
          'desc': d.get('bucketDescription', '').strip(),
      }

    for code, d in definitions['Class'].iteritems():
      self[code] = {
          'name': d['className'].strip(),
      }

    for code, d in definitions['Gender'].iteritems():
      self[code] = {
          'name': d['genderName'].strip(),
      }

    for code, d in definitions['InventoryItem'].iteritems():
      self[code] = {
          'name': d.get('itemName', '').strip() or 'Item #%i' % code,
          'desc': d.get('itemDescription', '').strip(),
          'type': d['bucketTypeHash'],
          'icon': d['icon'].strip(),
          'perks': d['perkHashes'],
      }

    for code, d in definitions['SandboxPerk'].iteritems():
      self[code] = {
          'name': (d.get('displayName') or str(code)).strip(),
          'desc': d.get('displayDescription', '').strip(),
      }

    for code, d in definitions['Progression'].iteritems():
      self[code] = {
          'name': d['name'].strip().replace('.', '_'),
          'icon': d.get('icon', '').strip(),
      }

    for code, d in definitions['Race'].iteritems():
      self[code] = {
          'name': d['raceName'].strip(),
      }

    for code, d in definitions['Stat'].iteritems():
      self[code] = {
          'name': d.get('statName', '').strip() or 'Stat #%i' % code,
      }

  def __missing__(self, k):
    return {'name': '#%i' % k}
