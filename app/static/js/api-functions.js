/**
 * Created by koyexes on 21/04/2017.
 */
var user_data, total_long_urls, total_shorten_urls,shorten_urls;
var functions = {
    get_total_shorten_urls: function (token, successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/shorten-urls/total',
            async: false,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
            },
            success: function (data) {
                shorten_urls = data;
                if(successCallback) successCallback();
            },
            error: function (error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },
    get_shorten_urls: function (token, successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/shorten-urls',
            async: false,
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
            },
            success: function (data) {
                shorten_urls = data;
                if(successCallback) successCallback();
            },
            error: function (error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },
    get_total_long_urls: function (token, successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/urls/total',
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
            },
            success: function (data) {
                total_long_urls = data;
                if (successCallback) successCallback()
            },
            error: function (error) {
               templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    get_user: function (token, successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/profile',
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
            },
            success: function (data) {
                user_data = data;
                if(successCallback) successCallback();
            },
            error: function (error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    refreshToken: function (user_data, successCallback) {
         $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/'+ user_data["username"] + '/' + user_data["id"] +'/token/refresh',
            success: function (data) {
                window.localStorage.setItem("token", data["token"]);
                templateRenders.renderTopNavigation(data);
                if (successCallback) successCallback();
            },
            error: function (error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    checkTokenValidity: function (successCallback, refreshCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/token/'+ window.localStorage.getItem("token") + '/validity',
            success: function (data) {
                if (data.is_valid &&  successCallback ){
                    successCallback();
                } else if(data.is_valid && refreshCallback) {
                    templateRenders.renderAlert("alert-danger", "Token still valid", "You can't refresh a valid token" );
                }else {
                    functions.getCredentials(refreshCallback, successCallback);
                }

            },
            error: function (error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    getCredentials: function (refreshCallback, successCallback) {
        $.get( "/credentials", {} )
            .done(function(data) {
                if (refreshCallback) refreshCallback(JSON.parse(data), successCallback);
            });
    },

    shortenUrl: function(successCallback) {
        var values = {};
        $('#shortenUrlForm :input').each(function () {
            if ($(this).val()){
                values[this.name] = $(this).val();
            };

        });
        var token = window.localStorage.getItem("token");
        $.ajax({
            type: 'POST',
            data: JSON.stringify(values),
            contentType: 'application/json',
            url: '/api/v1.0/url/shorten/',
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Basic " + base64.encode(token + ":" + ""));
            },
            success: function (data) {
                $('#shortenUrlModal').modal('hide');
                templateRenders.renderAlert("alert-info", data["message"]+": ", data["shorten_url"]["shorten_url_name"]);
                functions.get_total_long_urls(token, function () {
                    functions.get_total_shorten_urls(token, function () {
                        templateRenders.renderLeftAsideNavigation(total_long_urls, total_shorten_urls)
                        if(successCallback) successCallback();
                    });
                });
            },
            error: function (error) {
                $('#shortenUrlModal').modal('hide');
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    }
};

