# Copyright 2014 Daniel Reed <n@ml.org>

import jinja2
import json
import pprint
import webapp2
from base import bungie
from base.bungie import destiny
from base.bungie.destiny import manifest
from base.bungie.destiny import user as destiny_user


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class DBPage(webapp2.RequestHandler):
  def get(self):
    defs = manifest.GetDef()
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_index.html').render({
        'breadcrumbs': (
            ('/db/', 'DB'),
        ),
        'defs': defs,
    }))


class DBBucketPage(webapp2.RequestHandler):
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


class DBObjectPage(webapp2.RequestHandler):
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


class IndexPage(webapp2.RequestHandler):
  def get(self):
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/index.html').render({
        'breadcrumbs': (),
    }))


class UserHTMLPage(webapp2.RequestHandler):
  def get(self, username):
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/user.html').render({
        'breadcrumbs': (
            ('/' + username, username),
        ),
        'username': username,
    }))


class UserJSONPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'application/json'
    self.response.write(json.dumps(user, sort_keys=True))


class UserPyPage(webapp2.RequestHandler):
  def get(self, username):
    user = destiny_user.User(username)
    self.response.headers['content-type'] = 'text/plain'
    self.response.write(pprint.pformat(user))


class UserRawPage(webapp2.RequestHandler):
  def get(self, username):
    username, accounttype, accountid, summary = destiny_user.GetDestinyUser(username)
    self.response.content_type = 'text/html'
    self.response.write(JINJA2.get_template('dashboard/db_object.html').render({
        'breadcrumbs': (
            ('/%s.raw' % username, username),
        ),
        'obj': summary,
    }))


class Warmup(webapp2.RequestHandler):
  def get(self):
    pass


app = webapp2.WSGIApplication([
    ('/_ah/warmup', Warmup),
    ('/', IndexPage),
    ('/db/?', DBPage),
    ('/db/([a-zA-Z]+)/?', DBBucketPage),
    ('/db/([a-zA-Z]+)/([0-9]+)/?', DBObjectPage),
    ('/([a-zA-Z0-9-_ ]+)', UserHTMLPage),
    ('/([a-zA-Z0-9-_ ]+)[.]json', UserJSONPage),
    ('/([a-zA-Z0-9-_ ]+)[.]py', UserPyPage),
    ('/([a-zA-Z0-9-_ ]+)[.]raw', UserRawPage),
], debug=True)
