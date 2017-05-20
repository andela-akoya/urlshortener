var jwt_decoder = function(token) {
    var base64Url = token.split('.')[0];
    var base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse(window.atob(base64));
};

$.ajaxSetup({
    contentType: 'application/json'
});
// registration authentication
$('#signupForm').on('submit', function(e) {
    e.preventDefault();
    var values = {};
    $('#signupForm :input').each(function() {
        values[this.name] = $(this).val();
    });

    $.ajax({
        type: 'POST',
        data: JSON.stringify(values),
        contentType: 'application/json',
        url: '/api/v1.0/register/',
        success: function(data) {
            $('#signupModal').modal('close');
            Materialize.toast(data.message, 1000, 'rounded', function() { window.location.href = '/login' });
            $('#toast-container div').css("background-color", "#388e3c");
        },
        error: function(error) {
            Materialize.toast(JSON.parse(error.responseText).message, 4000, 'rounded');
            $('#toast-container div').css("background-color", "#d32f2f");
        }
    });
});

// login  authentication
$('#loginForm').on('submit', function(e) {
    e.preventDefault();
    var values = {};
    $('#loginForm :input').each(function() {
        values[this.name] = $(this).val();
    });
    $.ajax({
        type: 'POST',
        data: JSON.stringify(values),
        contentType: 'application/json',
        url: '/api/v1.0/token',
        beforeSend: function(xhr) {
            xhr.setRequestHeader("Authorization", "Basic " + base64.encode(values.username + ":" + values.password));
        },
        success: function(data) {
            window.localStorage.setItem("token", data.token);
            var payload = jwt_decoder(data.token);
            payload.exp = new Date((1000 * payload.exp) + (1000 * 60 * 60)).toUTCString();
            $('#loginModal').modal('close');
            Materialize.toast(data.message, 1000, 'rounded', function() {
                functions.get_total_long_urls(function() {
                    functions.get_total_shorten_urls(function() {
                        functions.get_user(function() {
                            data = Object.assign(data, user_data, total_long_urls, total_shorten_urls, payload);
                            console.log(data);
                            $.post("/start_session/", JSON.stringify(data))
                                .done(function(data) {
                                    window.location.href = "/main/dashboard";
                                    window.history.pushState("/main/dashboard", "Dashboard", "/main/dashboard");
                                });
                        });
                    });
                });
            });

            $('#toast-container div').css("background-color", "#388e3c");
        },
        error: function(error) {
            Materialize.toast(JSON.parse(error.responseText).message, 4000, 'rounded');
            $('#toast-container div').css("background-color", "#d32f2f");
        }
    });
});

/*
 * this function listens to the submit event of the shortenUrlForm
 * and  triggers the shortenUrl function that handles the post request
 * of the form
 */
$("#shortenUrlForm").on('submit', function(e) {
    e.preventDefault();
    functions.shortenUrl();
});


// var shortenUrlByDate = function(e) {
//     functions.checkTokenValidity(urlTemplateMap["shorten-url/date-added"], functions.refreshToken);
// };