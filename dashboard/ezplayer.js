/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
ezplayer = window.ezplayer || {};


ezplayer.getPlayerByName = function(name, cb) {
  bungie.searchDestinyPlayer(name, function(rawAccounts) {
    var accounts = [];
    var chain = [];

    for (var i = 0; i < rawAccounts.length; i++) {
      var rawAccount = rawAccounts[i];
      var account = new ezplayer.Account(rawAccount.membershipType, rawAccount.membershipId,
                                         rawAccount.displayName);

      accounts.push(account);
      chain.push(account.getCharacters_.bind(account));
    }
    chain.push([cb, new ezplayer.Player(accounts)]);
    nmlorg.runChain(chain);
  }.bind(this));
};


ezplayer.Player = function(accounts) {
  this.accounts = accounts;
};


var ACCOUNT_TYPES_ = {
    1: {
        'code': 1,
        'icon': 'https://www.bungie.net/img/theme/destiny/icons/icon_xbl.png',
        'name': 'Xbox Live',
    },
    2: {
        'code': 2,
        'icon': 'https://www.bungie.net/img/theme/destiny/icons/icon_psn.png',
        'name': 'PlayStation Network',
    },
};


ezplayer.Account = function(typeCode, id, name) {
  this.type = ACCOUNT_TYPES_[typeCode];
  this.id = id;
  this.name = name;
};


ezplayer.Account.prototype.getCharacters_ = function(cb) {
  this.characters = ezbungie.getCharacters(this.type.code, this.id, function(characters) {
    this.characters = characters;
    cb();
  }.bind(this));
};

})();
