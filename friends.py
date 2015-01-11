# Copyright 2014 Daniel Reed <n@ml.org>

import collections
import jinja2
import time
import webapp2

import destiny


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class FriendsPage(webapp2.RequestHandler):
  def get(self):
    now = time.time()
    defs = destiny.Definitions()

    activities = collections.defaultdict(list)
    # TODO(n): Accept a username as a parameter and get that user's friends, instead of requiring
    # the list to be passed in via a query parameter.
    for username in self.request.get('friends').split(','):
      user = destiny.User(username, defs=defs)
      character = sorted(user['characters'].itervalues(),
                         key=lambda character: character['last_online'])[-1]
      if now - character['last_online'] > 600:
        activity = '~Offline'
      elif not character['current_activity']:
        activity = '~In Orbit'
      elif character['current_activity']['name'].startswith(character['current_activity']['type']):
        activity = character['current_activity']['name']
      else:
        activity = '%s: %s' % (character['current_activity']['type'], character['current_activity']['name'])

      activities[activity].append(character)
      activities[activity].sort(key=lambda character: -character['last_online'])

    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('friends.html').render({
            'activities': activities,
            'now': now,
        }))


app = webapp2.WSGIApplication([
    ('/friends', FriendsPage),
], debug=True)
