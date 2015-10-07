/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


/** @namespace */
nmlorg.ui = nmlorg.ui || {};


nmlorg.ui.icon = function(src, dim) {
  if (typeof(src) != 'string')
    src = src.icon;
  if (src[0] == '/')
    src = 'https://www.bungie.net' + src;
  var img = document.createElement('img');
  img.height = dim;
  img.src = src;
  return img;
};


nmlorg.ui.iconLine = function(icons, height) {
  var div = document.createElement('div');
  for (var i = 0; i < icons.length; i++) {
    var img = nmlorg.ui.icon(icons[i], height);
    div.appendChild(img);
    if (i)
      img.style.paddingLeft = Math.ceil(height / 4) + 'px';
  }
  return div;
};


nmlorg.ui.placard = function(data) {
  var div = document.createElement('div');
  div.style.backgroundColor = data.active ? '#212121' : '#636363';
  div.style.color = 'white';
  div.style.height = data.height + 'px';
  div.style.position = 'relative';
  div.style.width = '300px';
  var front = document.createElement('div');
  div.appendChild(front);
  front.style.height = div.style.height;
  front.style.overflow = 'hidden';
  front.style.position = 'relative';
  front.style.whiteSpace = 'nowrap';
  front.style.width = div.style.width;
  var offsets = {'left': 0, 'right': 0};
  if (data.icon) {
    front.appendChild(nmlorg.ui.icon(data.icon, data.height));
    offsets.left += data.height;
  }
  var numLines = Math.max(data.left ? data.left.length : 0, data.right ? data.right.length : 0);
  var lineHeightDiv = numLines * 2 + 1;
  for (var side in {'left': 1, 'right': 2}) {
    if (!data[side] || !data[side].length)
      continue;
    for (var i = 0; i < data[side].length; i++) {
      var line = data[side][i];
      if (!line)
        continue;
      var lineDiv = document.createElement('div');
      front.appendChild(lineDiv);
      var lineHeight = data.height * (i ? 2 : 3) / lineHeightDiv;
      var fontSize = Math.ceil(2 * lineHeight / 3);
      lineDiv.style.backgroundColor = div.style.backgroundColor;
      lineDiv.style.fontSize = fontSize + 'px';
      lineDiv.style.height = lineHeight + 'px';
      lineDiv.style.paddingLeft = lineDiv.style.paddingRight = '2px';
      lineDiv.style.position = 'absolute';
      lineDiv.style.top = (i ? data.height * (1 + i * 2) / lineHeightDiv : 0) + 'px';
      lineDiv.style[side] = offsets[side] + 'px';
      if (typeof(line) == 'string')
        lineDiv.textContent = line;
      else if (line instanceof Array)
        lineDiv.appendChild(nmlorg.ui.iconLine(line, fontSize));
      else
        lineDiv.appendChild(line);
    }
  }
  if (data.drawer || data.link) {
    var drawer = document.createElement('div');
    div.appendChild(drawer);
    drawer.style.backgroundColor = '#dedede';
    drawer.style.border = '5px solid ' + div.style.backgroundColor;
    drawer.style.color = div.style.backgroundColor;
    drawer.style.display = 'none';
    drawer.style.fontSize = '10px';
    drawer.style.left = '10px';
    drawer.style.padding = '3px';
    drawer.style.position = 'absolute';
    drawer.style.top = div.style.height;
    drawer.style.width = '280px';
    drawer.style.zIndex = 1;
    div.style.cursor = 'pointer';
    div.addEventListener('click', function() {
      drawer.style.display = drawer.style.display == '' ? 'none' : '';
    });
    for (var i = 0; i < data.drawer.length; i++) {
      var line = data.drawer[i];
      if (line instanceof Array) {
        for (var j = 0; j < line.length; j++) {
          var item = line[j];
          if (item.icon)
            drawer.appendChild(nmlorg.ui.icon(item, 10));
          else
            drawer.appendChild(document.createTextNode('\u2002'));
          drawer.appendChild(document.createTextNode(' ' + item.name));
          drawer.appendChild(document.createElement('br'));
        }
      } else {
        drawer.appendChild(document.createTextNode(line || ''));
        drawer.appendChild(document.createElement('br'));
      }
    }
    if (data.link) {
      if (data.drawer && data.drawer.length)
        drawer.appendChild(document.createElement('br'));
      var a = document.createElement('a');
      drawer.appendChild(a);
      a.href = data.link;
      a.textContent = 'DB definition';
    }
  }
  return div;
};


nmlorg.ui.bounty = function(bounty) {
  return nmlorg.ui.placard({
      'active': true,
      'height': 40,
      'icon': bounty.icon,
      'left': [
          bounty.name,
          bounty.desc,
      ],
      'right': [
          bounty.rewards,
      ],
      'drawer': [
          bounty.name,
          '',
          bounty.desc,
          '',
          'Rewards:',
          bounty.rewards,
      ],
      'link': '/db/InventoryItem/' + bounty.hash,
  });
};


nmlorg.ui.character = function(character) {
  var div = document.createElement('div');
  div.className = 'emblem';
  div.style.backgroundImage = "url('https://www.bungie.net" + character.emblem_banner + "')";

  var img = document.createElement('img');
  div.appendChild(img);
  img.src = 'https://www.bungie.net' + character.emblem_icon;

  var classDiv = document.createElement('div');
  div.appendChild(classDiv);
  classDiv.className = 'class';
  classDiv.textContent = character.class;

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

  var statsDiv = document.createElement('div');
  div.appendChild(statsDiv);
  statsDiv.className = 'stats';
  var norm = (character.stats.Agility + character.stats.Armor + character.stats.Recovery) / 100;
  var stats = [[100 + Math.round(character.stats.Agility / norm), 'Agility'],
               [100 + Math.round(character.stats.Armor / norm), 'Armor'],
               [100 + Math.round(character.stats.Recovery / norm), 'Recovery']];
  stats.sort();
  statsDiv.textContent = stats[2][1] + ' > ' + stats[1][1] + ' > ' + stats[0][1];
  statsDiv.title = (stats[2][0] - 100) + '% > ' + (stats[1][0] - 100) + '% > ' + (stats[0][0] - 100) + '%';

  div.title = levelDiv.textContent + ' ' + subDiv.textContent + ' ' + classDiv.textContent + ' ' +
      lightDiv.textContent + '\n\nProgress:';
  for (var i = 0; i < character.progress.length; i++) {
    var prog = character.progress[i];
    if (prog.current)
      div.title += '\n- ' + prog.name + ': ' + prog.current;
  }

  return div;
};


nmlorg.ui.item = function(item) {
  var div = document.createElement('a');
  div.className = 'item';
  if (item.equipped)
    div.className += ' active';
  div.href = '/db/InventoryItem/' + item.hash;

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
  var subs = [];
  if (item.class)
    subs.push(item.class)
  if (item.tier && (item.tier != 'Common'))
    subs.push(item.tier);
  if (subs.length) {
    subs.sort();
    subtitleDiv.textContent += ' (' + subs.join(', ') + ')';
  }

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

  var perkDiv = document.createElement('div');
  div.appendChild(perkDiv);
  perkDiv.className = 'perks';
  var perks = [];
  for (var i = 0; i < item.perks.length; i++)
    perks.push(item.perks[i].name);
  perkDiv.textContent = perks.join(' \u2022 ');

  div.title = titleDiv.textContent + (item.quantity > 1 ? ' (x ' + item.quantity + ')' : '') + '\n' +
      subtitleDiv.textContent + '\n' +
      statDiv.textContent + ' ' + statTypeDiv.textContent + (item.fully_upgraded ? '' : ' (in progress)') + '\n' +
      '\n' + item.desc;
  if (item.perks.length) {
    div.title += '\n\nPerks:';
    for (var i = 0; i < item.perks.length; i++)
      div.title += '\n- ' + item.perks[i].name + ': ' + item.perks[i].desc;
  }

  return div;
};


nmlorg.ui.quest = function(quest) {
  var parent = document.createElement('div');

  var div = document.createElement('div');
  parent.appendChild(div);
  div.className = 'quest';

  var img = document.createElement('img');
  div.appendChild(img);
  img.src = 'https://www.bungie.net' + quest.icon;

  var titleDiv = document.createElement('div');
  div.appendChild(titleDiv);
  titleDiv.className = 'title';
  titleDiv.textContent = quest.name;

  var subtitleDiv = document.createElement('div');
  div.appendChild(subtitleDiv);
  subtitleDiv.className = 'subtitle';
  subtitleDiv.textContent = quest.desc;

  div.title = titleDiv.textContent + '\n\n' + quest.desc;

  for (var i = 0; i < quest.steps.length; i++)
    parent.appendChild(nmlorg.ui.questStep(quest.steps[i]));

  return parent;
};


nmlorg.ui.questStep = function(step) {
  var div = document.createElement('a');
  div.className = 'quest-step';
  if (step.active)
    div.className += ' active';
  div.href = '/db/InventoryItem/' + step.hash;
  div.textContent = step.objective;
  for (var i = step.rewards.length - 1; i >= 0; i--) {
    var reward = step.rewards[i];
    var img = document.createElement('img');
    div.insertBefore(img, div.firstChild);
    img.src = 'https://www.bungie.net' + reward.icon;
    img.height = 10;
    img.style.paddingRight = '2px';
    img.title = reward.name;
  }
  div.title = step.name + '\n\n' + step.objective + '\n';
  for (var i = 0; i < step.objectives.length; i++) {
    var objective = step.objectives[i];
    if (objective.count > 1)
      div.title += '- ' + objective.count + ' ' + objective.name + '\n';
    else
      div.title += '- ' + objective.name + '\n';
  }
  div.title += '\n' + step.desc;
  return div;
};

})();
