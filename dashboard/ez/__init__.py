# Copyright 2015 Daniel Reed <n@ml.org>

from base.bungie import bungienet
from dashboard import base_app


class TransferItem(base_app.RequestHandler):
  def post(self):
    item_hash = self.request.get('hash')
    item_id = self.request.get('id')
    quantity = long(self.request.get('quantity'))
    accounttype = int(self.request.get('accounttype'))
    from_char = self.request.get('from')
    to_char = self.request.get('to')
    if from_char:
      bungienet.TransferItem(accounttype, from_char, item_hash, item_id, quantity, True)
    if to_char:
      bungienet.TransferItem(accounttype, to_char, item_hash, item_id, quantity, False)
    self.response.write('1')


app = base_app.WSGIApplication([
    ('/ez/TransferItem/?', TransferItem),
], debug=True)
