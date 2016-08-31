# Copyright 2015 Daniel Reed <n@ml.org>

from base.bungie import manifest
from dashboard import base_app


class BlankPage(base_app.RequestHandler):
  def get(self):
    manifest.DestinyDefinition.Blank()
    return self.redirect('/')


class PreloadPage(base_app.RequestHandler):
  def get(self):
    for group in manifest.GetDef():
      for code in manifest.GetDef(group):
        manifest.GetDef(group, code)


app = base_app.WSGIApplication([
    ('/admin/blank', BlankPage),
    ('/admin/preload', PreloadPage),
], debug=True)
