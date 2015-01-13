/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


nmlorg.fetch = function(url, cb) {
  var req = new XMLHttpRequest();

  if (cb) {
    req.open('GET', url, true);
    req.addEventListener('load', function(ev) {
      if (req.status == 200)
        cb(JSON.parse(req.responseText));
    });
  } else
    req.open('GET', url, false);

  req.send();
  if (req.status == 200)
    return JSON.parse(req.responseText);
};


/** @namespace */
nmlorg.destiny = nmlorg.destiny || {};


nmlorg.destiny.User = function(username) {
  this.name = username;
};


nmlorg.destiny.User.prototype.get = function(cb) {
  nmlorg.fetch('/data/getuser/' + this.name, function(data) {
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


nmlorg.destiny.User.prototype.getActive = function() {
  var characters = [];

  for (var characterId in this.characters) {
    var character = this.characters[characterId];

    characters.push([character.last_online, character]);
  }

  characters.sort();
  return new nmlorg.destiny.Character(this, characters[characters.length - 1][1]);
};


nmlorg.destiny.Character = function(user, data) {
  for (var k in data)
    this[k] = data[k];
  this.user = user;
};


nmlorg.destiny.Character.prototype.makeBanner = function(html) {
  var div = document.createElement('div');

  div.className = 'banner';
  if (Date.now() / 1000 - this.last_online > 600) {
    div.style.backgroundImage = '';
    this.title = 'Last: ' + new Date(this.last_online * 1000).toLocaleString();
  } else {
    div.style.backgroundImage = 'url(https://www.bungie.net' + this.emblem_banner + ')';
    this.title = this.level + ' ' + this.race + ' ' + this.gender + ' ' + this.class;
  }

  var img = document.createElement('img');

  div.appendChild(img);
  img.className = 'emblem';
  img.src = 'https://www.bungie.net' + this.emblem_icon;

  if (html) {
    html = html.split(/{{([^}]*)}}/);

    var res = [html[0]];

    for (var i = 1; i < html.length; i += 2) {
      var path = html[i].split('.');
      var cur = this;

      for (var j = 0; j < path.length; j++)
        cur = cur[path[j]];

      res.push(cur);
      res.push(html[i + 1]);
    }

    var htmlDiv = document.createElement('div');

    div.appendChild(htmlDiv);
    htmlDiv.innerHTML = res.join('');
  }
  
  return div;
};

})();
