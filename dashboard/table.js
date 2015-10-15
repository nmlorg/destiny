/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


/** @namespace */
nmlorg.table = nmlorg.table || {};


nmlorg.table.Table = function() {
  this.table_ = document.createElement('table');
  this.table_.className = 'table';
  this.thead_ = document.createElement('thead');
  this.table_.appendChild(this.thead_);
  this.tbody_ = document.createElement('tbody');
  this.table_.appendChild(this.tbody_);
};


nmlorg.table.Table.prototype.push = function(toHead) {
  var row = new nmlorg.table.Row();
  if (toHead)
    this.thead_.appendChild(row.render());
  else
    this.tbody_.appendChild(row.render());
  return row;
};


nmlorg.table.Table.prototype.render = function() {
  return this.table_;
};


nmlorg.table.Row = function() {
  this.tr_ = document.createElement('tr');
};


nmlorg.table.Row.prototype.render = function() {
  return this.tr_;
};


nmlorg.table.Row.prototype.push = function(cell) {
  var td = document.createElement('td');
  this.tr_.appendChild(td);
  if (typeof(cell) == 'string')
    td.innerHTML = cell;
  else
    td.appendChild(cell);
};


nmlorg.table.ListCell = function(label) {
  this.label_ = label || '';
  this.div_ = document.createElement('div');
  this.items_ = document.createElement('div');
  this.div_.appendChild(this.items_);
  this.itemsObserver_ = new MutationObserver(function(mutations) {
    if (this.items_.children.length == 1) {
      this.div_.style.cursor = '';
      this.toggle_.style.display = 'none';
    } else {
      this.div_.style.cursor = 'pointer';
      this.toggle_.style.display = '';
      this.toggle_.textContent = this.toggle_.textContent[0] + ' ' + this.items_.children.length + ' ' + this.label_;
    }
  }.bind(this));
  this.itemsObserver_.observe(this.items_, {'childList': true});
  this.toggle_ = document.createElement('div');
  this.div_.appendChild(this.toggle_);
  this.toggle_.style.display = 'none';
  this.toggle_.textContent = '\u25b2';
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
    if (item.dataset.sortKey < this.items_.children[i].dataset.sortKey) {
      this.items_.insertBefore(item, this.items_.children[i]);
      break;
    }
  if (i == this.items_.children.length)
    this.items_.appendChild(item);
};


nmlorg.table.ListCell.prototype.render = function() {
  return this.div_;
};

})();
