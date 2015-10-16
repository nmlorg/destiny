# Copyright 2015 Daniel Reed <n@ml.org>

from base.bungie import destiny
from dashboard import base_app


class APIPage(base_app.RequestHandler):
  def get(self):
    self.response.render('dashboard/api.html')


class TransferPage(base_app.RequestHandler):
  def post(self):
    item_hash = self.request.get('hash')
    item_id = self.request.get('id')
    quantity = long(self.request.get('quantity'))
    accounttype = int(self.request.get('accounttype'))
    from_char = self.request.get('from')
    to_char = self.request.get('to')
    if from_char:
      destiny.TransferItem(accounttype, from_char, item_hash, item_id, quantity, True)
      print 'Transferred from %r to Vault.' % from_char
    if to_char:
      destiny.TransferItem(accounttype, to_char, item_hash, item_id, quantity, False)
      print 'Transferred from Vault to %r.' % to_char
    self.response.write('1')


app = base_app.WSGIApplication([
    ('/api/?', APIPage),
    ('/api/TransferItem', TransferPage),
], debug=True)
