/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
ezbungie = window.ezbungie || {};


ezbungie.transferItem = function(itemHash, itemId, quantity, accountType, from, to, cb) {
  return nmlorg.fetch('/api/EZTransferItem', {
      'hash': itemHash,
      'id': itemId,
      'quantity': quantity,
      'accounttype': accountType,
      'from': from || '',
      'to': to || '',
  }, cb);
};

})();
