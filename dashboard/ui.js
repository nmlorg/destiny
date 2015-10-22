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
      if ((typeof(line) == 'string') || (typeof(line) == 'number'))
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
        var label = line[0];
        var lineData = line[1];
        var format = line[2] || '{name}';

        if (lineData instanceof Array) {
          var tmp = {};
          for (var j = 0; j < lineData.length; j++)
            tmp[lineData[j].name] = lineData[j];
          lineData = tmp;
        }
        var first = true;
        for (var name in lineData) {
          if (first) {
            first = false;
            drawer.appendChild(document.createElement('br'));
            drawer.appendChild(document.createTextNode(label));
            drawer.appendChild(document.createElement('br'));
          }
          var item = lineData[name];
          if (item instanceof Object) {
            if (item.icon)
              drawer.appendChild(nmlorg.ui.icon(item, 10));
            else
              drawer.appendChild(document.createTextNode('\u2022'));
            drawer.appendChild(document.createTextNode(' '));
            var tmp = format.split(/{([^}]*)}/g);
            drawer.appendChild(document.createTextNode(tmp[0]));
            for (var j = 1; j + 1 < tmp.length; j += 2) {
              drawer.appendChild(document.createTextNode(tmp[j] == 'name' ? name : item[tmp[j]]));
              drawer.appendChild(document.createTextNode(tmp[j + 1]));
            }
          } else
            drawer.appendChild(document.createTextNode('\u2022 ' + name + ': ' + item));
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


nmlorg.ui.activity = function(activity) {
  var steps = [];
  for (var i = 0; i < activity.steps.length; i++) {
    var step = activity.steps[i];
    step.status = step.complete ? '\u2611' : '\u2610';
    steps.push(step.status);
  }

  return nmlorg.ui.placard({
      'active': true,
      'height': 40,
      'icon': activity.icon,
      'left': [
          activity.name + (activity.complete ? ' \u2714' : ''),
          activity.period + ' ' + activity.type,
      ],
      'right': [
          steps.join(' '),
          activity.modifiers,
      ],
      'drawer': [
          activity.name,
          activity.period + ' ' + activity.type,
          '',
          activity.desc,
          ['Modifiers:', activity.modifiers],
          ['Steps:', activity.steps, '{status} {name}'],
          ['Rewards:', activity.rewards],
      ],
      'link': '/db/Activity/' + activity.hash,
  });
};


nmlorg.ui.bounty = function(bounty) {
  return nmlorg.ui.placard({
      'active': bounty.active,
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
          ['Objectives:', bounty.objectives, '{count} {name}'],
          ['Sources:', bounty.sources],
          ['Rewards:', bounty.rewards],
      ],
      'link': '/db/InventoryItem/' + bounty.hash,
  });
};


nmlorg.ui.character = function(character) {
  for (var name in character.progress) {
    var prog = character.progress[name];
    var progresses = [];
    prog.label = prog.level;
    if (prog.current && prog.next)
      prog.label += '.' + String(100 + Math.round(100 * prog.current / prog.next)).substr(1);
    if (prog.levels)
      prog.label += ' / ' + prog.levels;
    if (prog.daily)
      progresses.push(prog.daily + ' today');
    if (prog.weekly)
      progresses.push(prog.weekly + ' this week');
    if (progresses.length)
      prog.label += ' (' + progresses.join(', ') + ')';
  }

  return nmlorg.ui.placard({
      'active': true,
      'height': 96,
      'icon': character.emblem_icon,
      'left': [
          character.class,
          character.race + ' ' + character.gender,
      ],
      'right': [
          character.level,
          '\u2666 ' + character.light,
          character.progress.r1_s4_hiveship_orbs.level + ' / ' + character.progress.r1_s4_hiveship_orbs.levels,
      ],
      'drawer': [
          character.level + ' ' + character.race + ' ' + character.gender + ' ' +
              character.class + ' ' + character.light,
          ['Stats:', character.stats],
          ['Progress:', character.progress, '{name}: {label}'],
      ],
  });
};


var ITEM_NUM_ = 0;


nmlorg.ui.item = function(item) {
  var typeStr = item.type;
  var subs = [];
  if (item.class)
    subs.push(item.class)
  if (item.tier && (item.tier != 'Common'))
    subs.push(item.tier);
  if (subs.length) {
    subs.sort();
    typeStr += ' (' + subs.join(', ') + ')';
  }

  var statType = '';
  if (item.damage_type)
    statType = item.damage_type[0].toUpperCase() + item.damage_type.substr(1).toLowerCase();
  else if (item.primary_stat_type)
    statType = item.primary_stat_type;

  var div = nmlorg.ui.placard({
      'active': item.equipped,
      'height': 40,
      'icon': item.icon,
      'left': [
          item.name,
          typeStr,
          item.perks,
      ],
      'right': [
          item.primary_stat_value,
          statType,
          item.sources,
      ],
      'drawer': [
          item.name + (item.quantity > 1 ? ' (x ' + item.quantity + ')' : ''),
          typeStr,
          item.primary_stat_value ? item.primary_stat_value + ' ' + statType + (item.fully_upgraded ? '' : ' (in progress)') : '',
          '',
          item.desc,
          ['Perks:', item.perks, '{name}: {desc}'],
          ['Objectives:', item.objectives, '{count} {name}'],
          ['Sources:', item.sources],
      ],
      'link': item.id ? '/items/' + item.id : '/db/InventoryItem/' + item.hash,
  });

  if (item.quantity > 1) {
    var quantityDiv = document.createElement('div');
    div.appendChild(quantityDiv);
    quantityDiv.style.backgroundColor = 'white';
    quantityDiv.style.bottom = '0px';
    quantityDiv.style.color = 'black';
    quantityDiv.style.fontSize = '8px';
    quantityDiv.style.padding = '2px';
    quantityDiv.style.position = 'absolute';
    quantityDiv.textContent = item.quantity;
  }

  if (item.transferrable) {
    div.draggable = true;
    div.id = 'item-' + (++ITEM_NUM_);
    div.addEventListener('dragstart', function(e) {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('application/json', JSON.stringify({
          'divId': div.id,
          'item': item,
      }));
    });
  }

  return div;
};


nmlorg.ui.quest = function(quest) {
  var parent = document.createElement('div');
  parent.style.position = 'relative';

  parent.appendChild(nmlorg.ui.placard({
      'active': true,
      'height': 40,
      'icon': quest.icon,
      'left': [
          quest.name,
          quest.desc,
      ],
      'drawer': [
          quest.name,
          '',
          quest.desc,
      ],
      'link': '/db/InventoryItem/' + quest.hash,
  }));

  for (var i = 0; i < quest.steps.length; i++) {
    var step = nmlorg.ui.questStep(quest.steps[i]);
    parent.appendChild(step);
    step.style.marginBottom = step.style.marginTop = '1px';
  }

  return parent;
};


nmlorg.ui.questStep = function(step) {
  return nmlorg.ui.placard({
      'active': step.active,
      'height': 12,
      'left': [
          step.objective,
      ],
      'right': [
          step.rewards,
      ],
      'drawer': [
          step.name,
          '',
          step.objective,
          ['Objectives:', step.objectives, '{count} {name}'],
          ['Rewards:', step.rewards],
      ],
      'link': '/db/InventoryItem/' + step.hash,
  });
};

})();
