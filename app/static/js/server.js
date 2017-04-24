var user_data, long_urls, shorten_urls;
$.ajaxSetup({
  contentType: 'application/json'
});
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
        url: '/api/v1.0/register/',
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
        url: '/api/v1.0/token',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(values["username"] + ":" + values["password"]));
        },
        success: function (data) {
            window.localStorage.setItem("token", data["token"]);
            $('#loginModal').modal('close');
            Materialize.toast(data.message, 1000,'rounded', function () {
                var token = window.localStorage.getItem("token");
                get_long_urls(token, function(){
                    get_shorten_urls(token, function () {
                        get_user(token, function () {
                            data= Object.assign(data,user_data, long_urls, shorten_urls);
                            $.post( "/start_session/", JSON.stringify(data) )
                                .done(function (data) {
                                    $("body").empty().append(data);
                                    window.history.pushState("/dashboard", "Dashboard", "/dashboard" );
                                });
                        });
                    });
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

var get_shorten_urls = function (token, callback) {
    $.ajax({
        type: 'GET',
        data: {},
        contentType: 'application/json',
        url: '/api/v1.0/user/shorten-urls/',
        async: false,
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
        },
        success: function (data) {
            shorten_urls = data;
            if(callback) callback();
        },
        error: function (error) {
            console.log(error);
        }
    });
};

var get_long_urls = function (token, callback) {
    $.ajax({
        type: 'GET',
        data: {},
        contentType: 'application/json',
        url: '/api/v1.0/user/urls/',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
        },
        success: function (data) {
            long_urls = data;
            if (callback) callback()
        },
        error: function (error) {
            console.log(error);
        }
    });
};

var get_user = function (token, callback) {
    $.ajax({
        type: 'GET',
        data: {},
        contentType: 'application/json',
        url: '/api/v1.0/user/profile',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
        },
        success: function (data) {
            user_data = data
            if(callback) callback();
        },
        error: function (error) {
            console.log(error)
        }
    });
};

var refreshToken = function () {
     $.ajax({
        type: 'GET',
        data: {},
        contentType: 'application/json',
        url: '/api/v1.0/get_token',
        beforeSend: function (xhr) {
            xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(user_data["username"] + ":" + user_data["password"]));
        },
        success: function (data) {
            window.localStorage.setItem("token", data["token"]);
        },
        error: function (error) {
            console.log(error)
        }
    });
};

var checkTokenValidity = function (callback) {
    $.ajax({
        type: 'GET',
        data: {},
        contentType: 'application/json',
        url: '/api/v1.0/token/'+ window.localStorage.getItem("token") + '/validity',
        success: function (data) {
            console.log(data);
            callback()
        },
        error: function (error) {
            console.log(error);
        }
    });
};