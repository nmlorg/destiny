# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import json
import webapp2
from base.bungie import platform
from base.bungie.destiny import definitions
import db


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
I = 0


class UserPage(webapp2.RequestHandler):
  def get(self, username):
    bungie = platform.Bungie()
    defs = definitions.Definitions(bungie=bungie)
    user = db.DestinyUser.GetUser(username, bungie=bungie, defs=defs)

    def F(d, seen=()):
      global I

      I += 1

      self.response.write(' <code style="border: 1px solid black; cursor: pointer; display: inline-block; text-align: center; height: 1em; width: 1em" onclick="var st = document.getElementById(\'i%i\').style; if (st.display == \'none\') { st.display = \'\'; this.textContent = \'-\'; } else { st.display = \'none\'; this.textContent = \'+\'; }">+</code>' % I)

      if isinstance(d, dict):
        self.response.write('<ul style="display: none" id="i%i">' % I)
        for k, v in sorted(d.iteritems()):
          self.response.write('<li>%s:' % (k,))
          if isinstance(v, (dict, list, tuple)) and v:
            F(v, seen=seen)
          else:
            self.response.write(' ' + json.dumps(v))
            if k.endswith('Hash'):
              self.response.write(': ')
              if v in seen:
                self.response.write('[...]')
              elif v not in defs:
                self.response.write('[unknown]')
              else:
                F(defs[v], seen=seen + (v,))
          self.response.write('</li>')
        self.response.write('</ul>')
      else:
        self.response.write('<ol style="display: none" id="i%i">' % I)
        for v in d:
          self.response.write('<li>')
          if isinstance(v, (dict, list, tuple)) and v:
            F(v, seen=seen)
          else:
            self.response.write(json.dumps(v))
          self.response.write('</li>')
        self.response.write('</ol>')

    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('user.html').render({'user': user}))
    F({'simplified': user, 'raw': user.raw_account})


class Warmup(webapp2.RequestHandler):
  def get(self):
    pass


app = webapp2.WSGIApplication([
    ('/_ah/warmup', Warmup),
    ('/user/(.*)', UserPage),
], debug=True)
