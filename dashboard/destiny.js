/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


/** @namespace */
nmlorg.destiny = nmlorg.destiny || {};


nmlorg.destiny.User = function(username) {
  this.name = username;
};


nmlorg.destiny.User.prototype.get = function(cb) {
  nmlorg.fetch('/' + this.name + '.json', function(data) {
    for (var k in data)
      this[k] = data[k];

    this.account_type_icon = {
        1: 'https://www.bungie.net/img/theme/destiny/icons/icon_xbl.png',
        2: 'https://www.bungie.net/img/theme/destiny/icons/icon_psn.png',
    }[this.account_type];

    if (cb)
      cb();
  }.bind(this));
};


nmlorg.destiny.transferItem = function(itemHash, itemId, quantity, accountType, from, to, cb) {
  return nmlorg.fetch('/api/transfer', cb, {
      'hash': itemHash,
      'id': itemId,
      'quantity': quantity,
      'accounttype': accountType,
      'from': from || '',
      'to': to || '',
  });
};

})();
