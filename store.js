/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg.store = nmlorg.store || {};


/** @constructor */
nmlorg.store.Store = function(base) {
  this.base_ = base + '.';
};


nmlorg.store.Store.prototype.add = function(name, value) {
  var storedValue = localStorage.getItem(this.base_ + name);

  if (storedValue)
    value = JSON.parse(storedValue);

  Object.defineProperty(this, name, {
      'enumerable': true,
      'get': function() {
        return value;
      },
      'set': function(newValue) {
        value = newValue;
        localStorage.setItem(this.base_ + name, JSON.stringify(value));
      },
  });
};


})();
