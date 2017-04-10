// registration authentication
$('#signupForm').on('submit', function(e) {
    e.preventDefault();
    var values = {};
    $('#signupForm :input').each(function () {
        values[this.name] = $(this).val();
    });

    $.ajax({
        type: 'POST',
        data: JSON.stringify(values),
        contentType: 'application/json',
        url: '/api/register/',
        success: function (data) {
            $('#signupModal').modal('close');
            Materialize.toast(data.message, 1000,'rounded',function () {window.location.href = '/login'});
            $('#toast-container div').css("background-color", "#388e3c");
        },
        error: function (error) {
            Materialize.toast(JSON.parse(error.responseText).message, 4000, 'rounded');
            $('#toast-container div').css("background-color", "#d32f2f");
        }
    });
});

// login  authentication
$('#loginForm').on('submit', function(e) {
    e.preventDefault();
    var values = {};
    $('#loginForm :input').each(function () {
        values[this.name] = $(this).val();
    });
    $.ajax({
        type: 'GET',
        data: JSON.stringify(values),
        contentType: 'application/json',
        url: '/api/token',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(values["username"] + ":" + values["password"]));
        },
        success: function (data) {
            $('#loginModal').modal('close');
            Materialize.toast(data.message, 1000,'rounded', function () {
                $('body').load("/dashboard", data, function(){
                    window.history.pushState("/dashboard", "Dashboard", "/dashboard" );
                });
            });

            $('#toast-container div').css("background-color", "#388e3c");
        },
        error: function (error) {
            Materialize.toast(JSON.parse(error.responseText).message, 4000, 'rounded');
            $('#toast-container div').css("background-color", "#d32f2f");
        }
    });
});

