/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


/** @namespace */
nmlorg.table = nmlorg.table || {};


nmlorg.table.Table = function() {
  this.headRows_ = [];
  this.bodyRows_ = [];
};


nmlorg.table.Table.prototype.push = function(toHead) {
  var row = [];
  if (toHead)
    this.headRows_.push(row);
  else
    this.bodyRows_.push(row);
  return row;
};


nmlorg.table.Table.prototype.render = function() {
  var table = document.createElement('table');
  table.className = 'table';
  var thead = document.createElement('thead');
  table.appendChild(thead);
  this.render_(this.headRows_, thead);
  var tbody = document.createElement('tbody');
  table.appendChild(tbody);
  this.render_(this.bodyRows_, tbody);
  return table;
};


nmlorg.table.Table.prototype.render_ = function(rows, parent) {
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var tr = document.createElement('tr');
    parent.appendChild(tr);
    for (var j = 0; j < row.length; j++) {
      var cell = row[j];
      var td = document.createElement('td');
      tr.appendChild(td);
      if (typeof(cell) == 'string')
        td.innerHTML = cell;
      else
        td.appendChild(cell);
    }
  }
};


nmlorg.table.ListCell = function(label) {
  this.label_ = label || '';
  this.div_ = document.createElement('div');
  this.items_ = document.createElement('div');
  this.div_.appendChild(this.items_);
  this.toggle_ = document.createElement('div');
  this.div_.appendChild(this.toggle_);
  this.toggle_.style.display = 'none';
  this.toggle_.addEventListener('click', function() {
    if (this.items_.children.length > 1) {
      if (this.items_.style.display == '') {
        this.items_.style.display = 'none';
        this.toggle_.textContent = '\u25b6' + this.toggle_.textContent.substr(1);
      } else {
        this.items_.style.display = '';
        this.toggle_.textContent = '\u25b2' + this.toggle_.textContent.substr(1);
      }
    }
  }.bind(this));
};


nmlorg.table.ListCell.prototype.push = function(item, sortKey) {
  if (sortKey)
    item.dataset.sortKey = sortKey;

  for (var i = 0; i < this.items_.children.length; i++)
    if (sortKey < this.items_.children[i].dataset.sortKey) {
      this.items_.insertBefore(item, this.items_.children[i]);
      break;
    }
  if (i == this.items_.children.length)
    this.items_.appendChild(item);

  if (this.items_.children.length == 1) {
    this.div_.style.cursor = '';
    this.items_.style.display = '';
    this.toggle_.style.display = 'none';
  } else {
    this.div_.style.cursor = 'pointer';
    this.items_.style.display = 'none';
    this.toggle_.style.display = '';
    this.toggle_.textContent = '\u25b6 ' + this.items_.children.length + ' ' + this.label_;
  }
};


nmlorg.table.ListCell.prototype.render = function() {
  return this.div_;
};

})();
