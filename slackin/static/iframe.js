/*global io,data*/

(function(){

  // give up and resort to `target=_blank`
  // if we're not modern enough
  if (!document.body.getBoundingClientRect
   || !document.body.querySelectorAll
   || !window.postMessage) {
    return;
  }

  // the id for the script we capture
  var id;

  // listen on setup event from the parent
  // to set up the id
  window.addEventListener('message', function onmsg(e){
    if (/^slackin:/.test(e.data)) {
      id = e.data.replace(/^slackin:/, '');
      document.body.addEventListener('click', function(ev){
        var el = ev.target;
        while (el && 'A' != el.nodeName) el = el.parentNode;
        if (el && '_blank' == el.target) {
          ev.preventDefault();
          parent.postMessage('slackin-click:' + id, '*');
        }
      });
      window.removeEventListener('message', onmsg);

      // notify initial width
      refresh();
    }
  });

  // notify parent about current width
  var button = document.querySelector('.slack-button');
  var lastWidth;
  function refresh(){
    var width = button.getBoundingClientRect().width;
    if (top != window && window.postMessage) {
      var but = document.querySelector('.slack-button');
      var width = Math.ceil(but.getBoundingClientRect().width);
      if (lastWidth != width) {
        lastWidth = width;
        parent.postMessage('slackin-width:' + id + ':' + width, '*');
      }
    }
  }
})();
