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
}


nmlorg.table.Table.prototype.push = function(toHead) {
  var row = new nmlorg.table.Row_();
  if (toHead)
    this.headRows_.push(row);
  else
    this.bodyRows_.push(row);
  return row;
};


nmlorg.table.Row_ = function() {
  this.cells_ = [];
};


nmlorg.table.Row_.prototype.push = function(contents) {
  this.cells_.push(contents || []);
  return this.cells_[this.cells_.length - 1];
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
    var row = rows[i].cells_;
    var tr = document.createElement('tr');
    parent.appendChild(tr);
    for (var j = 0; j < row.length; j++) {
      var cell = row[j];
      var td = document.createElement('td');
      tr.appendChild(td);
      if (typeof(cell) == 'string')
        td.innerHTML = cell;
      else if (cell instanceof HTMLElement)
        td.appendChild(cell);
      else if (cell.length == 1)
        td.appendChild(cell[0]);
      else if (cell.length > 1) {
        var itemDiv = document.createElement('div');
        td.appendChild(itemDiv);
        itemDiv.style.display = 'none';
        for (var k = 0; k < cell.length; k++)
          itemDiv.appendChild(cell[k]);
        var toggleDiv = document.createElement('div');
        td.appendChild(toggleDiv);
        toggleDiv.style.cursor = 'pointer';
        toggleDiv.textContent = '\u25b6 ' + cell.length + ' ' + row[0];
        if (toggleDiv.textContent[toggleDiv.textContent.length - 1] != 's')
          toggleDiv.textContent += 's';
        toggleDiv.addEventListener('click', function() {
          var itemDiv = this.previousElementSibling;
          if (itemDiv.style.display == '') {
            itemDiv.style.display = 'none';
            this.textContent = '\u25b6' + this.textContent.substr(1);
          } else {
            itemDiv.style.display = '';
            this.textContent = '\u25b2' + this.textContent.substr(1);
          }
        });
      }
    }
  }
};

})();
