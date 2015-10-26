# Copyright 2015 Daniel Reed <n@ml.org>

import jinja2
import webapp2
from base.bungie import auth
from base.bungie import bungienet
from base.util import fetch
from google.appengine.api import users
from google.appengine.ext import ndb


JINJA2 = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))


class User(ndb.Model):
  username = ndb.StringProperty()
  bungled = ndb.TextProperty()
  bungleatk = ndb.TextProperty()

  _profile = None

  @property
  def profile(self):
    if self._profile is None:
      self._profile = bungienet.GetCurrentUser()
    return self._profile


RequestHandler = webapp2.RequestHandler


class Request(webapp2.Request):
  user = None


class RequestContext(webapp2.RequestContext):
  def __enter__(self):
    request, response = super(RequestContext, self).__enter__()
    current_user = users.get_current_user()
    if current_user is not None:
      email = current_user.email().lower()
      request.user = response.user = User.get_by_id(email) or User(id=email)
      fetch.SetOpener(auth.BuildOpener(request.user.bungled, request.user.bungleatk))
    return request, response


class Response(webapp2.Response):
  user = None

  def render(self, fname, context=None):
    self.content_type = 'text/html'
    if context is None:
      context = {}
    if 'breadcrumbs' not in context:
      context['breadcrumbs'] = ()
    context['login_url'] = users.create_login_url()
    context['user'] = self.user
    self.write(JINJA2.get_template(fname).render(context))


class WSGIApplication(webapp2.WSGIApplication):
  request_class = Request
  request_context_class = RequestContext
  response_class = Response
