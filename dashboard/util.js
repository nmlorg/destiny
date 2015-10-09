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

})();
