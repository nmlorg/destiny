/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


/** @namespace */
nmlorg.ui = nmlorg.ui || {};


nmlorg.ui.banner = function(character) {
  var div = document.createElement('div');
  div.className = 'emblem';
  div.style.backgroundImage = "url('https://www.bungie.net" + character.emblem_banner + "')";

  var img = document.createElement('img');
  div.appendChild(img);
  img.src = 'https://www.bungie.net' + character.emblem_icon;

  var classDiv = document.createElement('div');
  div.appendChild(classDiv);
  classDiv.className = 'class';
  classDiv.textContent = character['class'];

  var subDiv = document.createElement('div');
  div.appendChild(subDiv);
  subDiv.className = 'subtitle';
  subDiv.textContent = character.race + ' ' + character.gender;

  var levelDiv = document.createElement('div');
  div.appendChild(levelDiv);
  levelDiv.className = 'level';
  levelDiv.textContent = character.level;

  var lightDiv = document.createElement('div');
  div.appendChild(lightDiv);
  lightDiv.className = 'light';
  lightDiv.textContent = '\u2666 ' + character.light;
  
  return div;
};


nmlorg.ui.item = function(item) {
  var div = document.createElement('div');
  div.className = 'item';

  var img = document.createElement('img');
  div.appendChild(img);
  img.src = 'https://www.bungie.net' + item.icon;

  if (item.quantity > 1) {
    var quantityDiv = document.createElement('div');
    div.appendChild(quantityDiv);
    quantityDiv.className = 'quantity';
    quantityDiv.textContent = item.quantity;
  }

  var titleDiv = document.createElement('div');
  div.appendChild(titleDiv);
  titleDiv.className = 'title';
  titleDiv.textContent = item.name;

  var subtitleDiv = document.createElement('div');
  div.appendChild(subtitleDiv);
  subtitleDiv.className = 'subtitle';
  subtitleDiv.textContent = item.type;
  if (item.tier && (item.tier != 'Common'))
    subtitleDiv.textContent += ' (' + item.tier + ')';

  var statDiv = document.createElement('div');
  div.appendChild(statDiv);
  statDiv.className = 'stat';
  if (item.primary_stat_value)
    statDiv.textContent = item.primary_stat_value;

  var statTypeDiv = document.createElement('div');
  div.appendChild(statTypeDiv);
  statTypeDiv.className = 'stat-type';
  if (item.damage_type)
    statTypeDiv.textContent = item.damage_type[0].toUpperCase() + item.damage_type.substr(1).toLowerCase() + ' ';
  else if (item.primary_stat_type)
    statTypeDiv.textContent += item.primary_stat_type;

  div.title = titleDiv.textContent + (item.quantity > 1 ? ' (x ' + item.quantity + ')' : '') + '\n' +
      subtitleDiv.textContent + '\n' +
      statDiv.textContent + ' ' + statTypeDiv.textContent + (item.fully_upgraded ? '' : ' (in progress)') + '\n' +
      '\n' + item.desc + '\n';
  for (var statName in item.stats) {
    var stat = item.stats[statName];
    if (stat[0] == stat[1])
      div.title += '\n' + statName + ': ' + stat[0];
    else
      div.title += '\n' + statName + ': ' + stat[0] + ' - ' + stat[1];
  }

  return div;
};

})();
