var max = 500;
function fetcher(url, pane, placeholder) {
  loader = MochiKit.Async.loadJSONDoc(url);
  var x = function (res) {
    status = res['status'];
    items = res['items'];
    if (items.length) {
      if (placeholder) {
	placeholder.style.display = 'none';
	placeholder = null;
      }
      for (var i in items) {
	var data = items[i];
	var trow = TR(null,
		      TD(null, data[0]),
		      TD({'class':'fixed'}, data[1]),
		      TD(null, data[2]),
		      TD(null, A({'href':data[3]}, 'link')));
	appendChildNodes(pane, trow);
      }
    }
    else if (status == 'done' && placeholder) {
      placeholder.className = 'noresults';
      placeholder.cells[0].innerHTML = 'No results.';
    }

    max = max - 1;
    if (status == 'ok' && max > 0) {
      callLater(0.50, function () { fetcher(url, pane, placeholder) });
    }
  };
  loader.addCallbacks(x, window.alert);
}
  

function setup() {
  var pane = document.getElementById('pane');
  var placeholder = document.getElementById('placeholder');
  var url = document.getElementById('queue_url').value;
  fetcher(url, pane, placeholder);
}

MochiKit.DOM.addLoadEvent(setup);



