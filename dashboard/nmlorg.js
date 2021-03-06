/**
 * @author Daniel Reed &lt;<a href="mailto:n@ml.org">n@ml.org</a>&gt;
 */

(function() {

/** @namespace */
nmlorg = window.nmlorg || {};


nmlorg.fetch = function(url, data, cb) {
  var method = data ? 'POST' : 'GET';
  var req = new XMLHttpRequest();

  if (cb) {
    req.open(method, url, true);
    req.addEventListener('load', function(ev) {
      if (req.status == 200)
        cb(JSON.parse(req.responseText));
    });
  } else
    req.open(method, url, false);

  if (data) {
    var fd = new FormData();
    for (var k in data)
      fd.append(k, data[k]);
    req.send(fd);
  } else
    req.send();
  if (req.status == 200)
    return JSON.parse(req.responseText);
};


nmlorg.runChain = function(chain) {
  var call = chain.shift();
  var args;

  if (call instanceof Array) {
    args = call;
    call = args.shift();
  } else
    args = [];
  if (chain.length)
    args.push(nmlorg.runChain.bind(null, chain));
  call.apply(null, args);
};

})();
