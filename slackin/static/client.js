/*global io,superagent*/

var body = document.body;
var request = superagent;

// elements
var select = body.querySelector('select');
var input = body.querySelector('input');
var button = body.querySelector('button');

// remove loading state
button.className = '';

// capture submit
body.addEventListener('submit', function(ev){
  ev.preventDefault();
  button.disabled = true;
  button.className = '';
  button.innerHTML = 'Please Wait';
  var channel = select ? select.value : null;
  invite(channel, input.value, function(err){
    if (err) {
      button.removeAttribute('disabled');
      button.className = 'error';
      button.innerHTML = err.message;
    } else {
      button.className = 'success';
      button.innerHTML = 'WOOT. Check your email!';
    }
  });
});


function invite(channel, email, fn){
  request
  .post('/invite')
  .send({
    channel: channel,
    email: email
  })
  .end(function(res){
    if (res.error) {
      var err = new Error(res.body.msg || 'Server error');
      return fn(err);
    } else {
      fn(null);
    }
  });
}

function update(val, n, noanim){
  var el = document.querySelector('.' + val);
  if (n != el.innerHTML) {
    el.innerHTML = n;
    anim(el, val);
  }
}

function anim(el, c){
  if (el.anim) return;
  el.className = c + ' grow';
  el.anim = setTimeout(function(){
    el.className = c;
    el.anim = null;
  }, 150);
}
