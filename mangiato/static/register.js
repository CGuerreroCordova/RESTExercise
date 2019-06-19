
$(document).ready(function() {
     $('form').on('submit', function(event) {
       $.ajax({
            data : JSON.stringify({
             first_name : $('#firstname').val(),
             last_name: $('#lastname').val(),
             username: $('#username').val(),
             password: $('#password').val(),
                 }),
             type : 'POST',
             url : "{{ url_for( 'Users.create_user' ) }}",
             dataType: 'text',
             contentType: "application/json; charset=utf-8",
            })
        .done(function(data) {
          $('#response').text(data.response).show();
      });
      });
});

