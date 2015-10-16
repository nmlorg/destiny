# Copyright 2015 Daniel Reed <n@ml.org>

from base.bungie import destiny
from dashboard import base_app


class Index(base_app.RequestHandler):
  def get(self):
    self.response.render('dashboard/api/index.html', {
        'breadcrumbs': (
            ('/api/', 'Bungie.net Platform API'),
        ),
        'endpoints': {
            'GetPublicXurVendor': (),
            'TransferItem': (
                ('hash', 'number', None, 'itemReferenceHash',
                 'The manifest code for all items with the same name.'),
                ('id', 'number', 0, 'itemId',
                 'The code for a specific instance of an item. Always 0 for stackable items.'),
                ('quantity', 'number', 1, 'stackSize',
                 'The number of items to transfer. Always 1 for non-stackable items.'),
                ('accounttype', 'number', 2, 'membershipType',
                 'The numeric membership type (1 = Xbox, 2 = PSN).'),
                ('from', 'text', None, 'characterId',
                 'The code for the character to take the item from. Empty when taking from the '
                 'vault.'),
                ('to', 'text', None, 'characterId',
                 'The code for the character to give the item to. Empty when storing in the '
                 'vault.'),
            ),
        },
    })


class GetPublicXurVendor(base_app.RequestHandler):
  def get(self):
    self.response.content_type = 'text/html'
    self.response.render('dashboard/db/object.html', {
        'breadcrumbs': (
            ('/api/', 'Bungie.net Platform API'),
            ('/api/GetPublicXurVendor', 'GetPublicXurVendor'),
        ),
        'obj': destiny.GetPublicXurVendor(),
    })

  post = get


class TransferItem(base_app.RequestHandler):
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
    ('/api/?', Index),
    ('/api/GetPublicXurVendor/?', GetPublicXurVendor),
    ('/api/TransferItem/?', TransferItem),
], debug=True)
