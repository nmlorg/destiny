# Copyright 2015 Daniel Reed <n@ml.org>

import json
from base.bungie import bungienet
from dashboard import base_app


ENDPOINTS = {
    'EquipItems': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
        ('itemids', 'numberlist', '6917529065725358993, 6917529067611239952', 'itemIds',
         '1 or more codes for specific instances of an item.'),
    ),
    'GetAccount': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
    ),
    'GetAccountSummary': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
    ),
    'GetActivityHistory': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
        ('mode', 'text', 'None', 'mode',
         'Game mode: AllArena, AllPvE, AllPvP, AllStrikes, Arena, ArenaChallenge, Control, '
         'Elimination, FreeForAll, Heroic, IronBanner, Lockdown, Mayhem, Nightfall, None, Patrol, '
         'PvPIntroduction, Raid, Rift, Story, Strike, Team, ThreeVsThree, TrialsOfOsiris, or '
         'ZoneControl. "None" returns all activities.'),
        ('count', 'number', 250, 'count',
         'Number of results to return (1 - 250).'),
        ('page', 'number', 0, 'page',
         'Page offset.'),
    ),
    'GetAdminsOfGroup': (
        ('groupid', 'number', 39966, 'groupId',
         'Numeric Bungie.net group code.'),
    ),
    'GetAdvisorsForCurrentCharacter': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetAllItemsSummary': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
    ),
    'GetAvailableLocales': (),
    'GetBungieAccount': (
        ('profileid', 'number', 6802287, 'membershipId',
         'Numeric Bungie.net profile code.'),
    ),
    'GetCharacter': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetCharacterActivities': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetCharacterInventory': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetCharacterProgression': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetCharacterSummary': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetCurrentUser': (),
    'GetDestinyAggregateActivityStats': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect.'),
    ),
    'GetDestinyManifest': (),
    'GetDestinySingleDefinition': (
        ('deftype', 'text', 'InventoryItem', 'definitionType',
         'Numeric code for the manifest chapter. See <a href="/db/">Destiny DB</a>.'),
        ('defid', 'number', 1274330687, 'definitionId',
         'Numeric code for the specific definition.'),
    ),
    'GetGlobalAlerts': (),
    'GetGrimoireByMembership': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
    ),
    'GetItemDetail': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
        ('accountid', 'number', 4611686018436064455, 'destinyMembershipId',
         'Numeric non-Bungie.net membership code.'),
        ('charid', 'number', 2305843009223046587, 'characterId',
         'Numeric code for the character to inspect. For items in the vault, use the id of any '
         'character owned by this account.'),
        ('itemid', 'number', 6917529065725358993, 'itemInstanceId',
         'Code for a specific instance of an item.'),
    ),
    'GetMyGrimoire': (
        ('accounttype', 'number', 2, 'membershipType',
         'Numeric non-Bungie.net membership type (1 = XBL, 2 = PSN).'),
    ),
    'GetPostGameCarnageReport': (
        ('activityid', 'number', 3966013892, 'activityId',
         "The activity's instanceId."),
    ),
    'GetPublicAdvisors': (),
    'GetPublicXurVendor': (),
    'GetSpecialEventAdvisors': (),
    'HelloWorld': (),
    'SearchDestinyPlayer': (
        ('username', 'text', 'nmlorg', 'displayName',
         'Non-Bungie.net username to search for.'),
    ),
    'SearchUsers': (
        ('username', 'text', 'nmlorg', 'q',
         'Bungie.net username to search for.'),
    ),
    'Settings': (),
}


class Index(base_app.RequestHandler):
  def get(self):
    self.response.render('dashboard/api/index.html', {
        'breadcrumbs': (
            ('/api/', 'Bungie.net Platform API'),
        ),
        'endpoints': ENDPOINTS,
    })


class Generic(base_app.RequestHandler):
  def get(self, callname):
    data = ENDPOINTS.get(callname)
    if data is None:
      return self.error(404)
    args = []
    for param, type, default, name, desc in data:
      arg = self.request.get(param)
      if type == 'number':
        arg = long(arg)
      elif type == 'numberlist':
        arg = map(long, arg.replace(',', ' ').split())
      args.append(arg)
    method = getattr(bungienet, callname)
    obj = method(*args)
    if 'text/html' not in self.request.headers.get('accept', ''):
      self.response.content_type = 'application/json'
      self.response.write(json.dumps(obj))
    else:
      self.response.content_type = 'text/html'
      self.response.render('dashboard/object.html', {
          'breadcrumbs': (
              ('/api/', 'Bungie.net Platform API'),
              ('/api/' + callname, callname),
          ),
          'obj': obj,
      })

  post = get


app = base_app.WSGIApplication([
    ('/api/?', Index),
    ('/api/(.*)/?', Generic),
], debug=True)
