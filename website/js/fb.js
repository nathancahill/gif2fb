window.video_id = null;
window.fbAsyncInit = function() {
FB.init({
  appId      : '239271859575863',
  status     : true,
  cookie     : true,
  xfbml      : true
});

FB.Event.subscribe('auth.authResponseChange', function(response) {
  if (response.status === 'connected') {
    login_callback();
  } else if (response.status === 'not_authorized') {
    FB.login(function(){}, {scope: 'video_upload'});
  } else {
    FB.login(function(){}, {scope: 'video_upload'});
  }
});
};

(function(d){
 var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
 if (d.getElementById(id)) {return;}
 js = d.createElement('script'); js.id = id; js.async = true;
 js.src = "//connect.facebook.net/en_US/all.js";
 ref.parentNode.insertBefore(js, ref);
}(document));

function login_callback() {
  mixpanel.track("Logged in");
  if (window.video_id !== null) {
      $('#generating').text('Posting');

      c = 1;

      var r = setInterval(function() {
          c += 1;

          $('#generating').text('Posting' + Array(c).join("."));

          if (c > 3) {
              c = 0;
          }
      }, 300);

      $.ajax({
          url: '/app/post',
          type: 'POST',
          data: {
              'id': window.video_id
          }
      }).done(function(data) {
          clearInterval(r);

          if (data == 'error') {
              mixpanel.track("Posting error");
              $('#generating').text('Failed :(');
          } else {
              mixpanel.track("Posted to Facebook");
              $('#generating').text('Posted.');
          }

          window.video_id = null;
      });
  }
}
