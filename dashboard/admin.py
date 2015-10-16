# Copyright 2015 Daniel Reed <n@ml.org>

from base.bungie.destiny import manifest
from dashboard import base_app


class BlankPage(base_app.RequestHandler):
  def get(self):
    manifest.DestinyDefinition.Blank()


app = base_app.WSGIApplication([
    ('/admin/blank', BlankPage),
], debug=True)
