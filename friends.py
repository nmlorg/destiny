# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import webapp2

import destiny


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class FriendsPage(webapp2.RequestHandler):
  def get(self):
    defs = destiny.Definitions()

    # TODO(n): Accept a username as a parameter and get that user's friends, instead of requiring
    # the list to be passed in via a query parameter.
    friends = []
    for username in self.request.get('friends').split(','):
      user = destiny.User(username, defs=defs)
      friends.append(sorted(user['characters'].itervalues(),
                            key=lambda character: character['last_online'])[-1])
    friends.sort(
        key=lambda character: character['current_activity'] and character['current_activity']['name'])

    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('friends.html').render({'friends': friends}))


app = webapp2.WSGIApplication([
    ('/friends', FriendsPage),
], debug=True)
