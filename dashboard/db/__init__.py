# Copyright 2014 Daniel Reed <n@ml.org>

from base.bungie.destiny import manifest
from dashboard import base_app


class IndexPage(base_app.RequestHandler):
  def get(self):
    defs = manifest.GetDef()
    self.response.render('dashboard/db/index.html', {
        'breadcrumbs': (
            ('/db/', 'DB'),
        ),
        'defs': defs,
    })


class BucketPage(base_app.RequestHandler):
  def get(self, bucket_name):
    bucket = manifest.GetDef(bucket_name)
    self.response.render('dashboard/db/bucket.html', {
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
        ),
        'bucket_name': bucket_name,
        'bucket': bucket,
    })


class ObjectPage(base_app.RequestHandler):
  def get(self, bucket_name, hashcode):
    hashcode = long(hashcode)
    obj = manifest.GetDef(bucket_name, hashcode)
    self.response.render('dashboard/db/object.html', {
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
            ('/db/%s/%i' % (bucket_name, hashcode), hashcode),
        ),
        'obj': obj,
    })


app = base_app.WSGIApplication([
    ('/db/?', IndexPage),
    ('/db/([a-zA-Z]+)/?', BucketPage),
    ('/db/([a-zA-Z]+)/([0-9]+)/?', ObjectPage),
], debug=True)
