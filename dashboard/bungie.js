/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
bungie = window.bungie || {};


bungie.getAccountSummary = function(accountType, accountId, cb) {
  return nmlorg.fetch('/api/GetAccountSummary', {
      'accounttype': accountType,
      'accountid': accountId,
  }, cb);
};


bungie.equipItems = function(accountType, charId, itemIds, cb) {
  return nmlorg.fetch('/api/EquipItems', {
      'accounttype': accountType,
      'charid': charId,
      'itemids': itemIds,
  }, cb);
};


bungie.searchDestinyPlayer = function(name, cb) {
  return nmlorg.fetch('/api/SearchDestinyPlayer', {
      'username': name,
  }, cb);
};

})();
