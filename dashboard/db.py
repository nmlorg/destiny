# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import webapp2
from base.bungie.destiny import manifest


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class IndexPage(webapp2.RequestHandler):
  def get(self):
    defs = manifest.GetDef()
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_index.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
        ),
        'defs': defs,
    }))


class BucketPage(webapp2.RequestHandler):
  def get(self, bucket_name):
    bucket = manifest.GetDef(bucket_name)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_bucket.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
        ),
        'bucket_name': bucket_name,
        'bucket': bucket,
    }))


class ObjectPage(webapp2.RequestHandler):
  def get(self, bucket_name, hashcode):
    hashcode = long(hashcode)
    obj = manifest.GetDef(bucket_name, hashcode)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_object.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
            ('/db/%s/' % bucket_name, bucket_name),
            ('/db/%s/%i' % (bucket_name, hashcode), hashcode),
        ),
        'obj': obj,
    }))


app = webapp2.WSGIApplication([
    ('/db/?', IndexPage),
    ('/db/([a-zA-Z]+)/?', BucketPage),
    ('/db/([a-zA-Z]+)/([0-9]+)/?', ObjectPage),
], debug=True)
