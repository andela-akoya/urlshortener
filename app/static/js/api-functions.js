/**
 * Created by koyexes on 21/04/2017.
 */
var user_data, total_long_urls, total_shorten_urls, shorten_urls;
var functions = {
    use_token_authentication: function(xhr) {
        xhr.setRequestHeader("Authorization", "Basic " + base64.encode(localStorage.getItem('token') + ":" + ""));
    },

    get_total_shorten_urls: function(successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/shorten-urls/total',
            async: false,
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                total_shorten_urls = data;
                if (successCallback) { successCallback(); }
            },
            error: function(error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    get_shorten_urls: function(successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/shorten-urls',
            async: false,
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                shorten_urls = data;
                if (successCallback) { successCallback(); }
            },
            error: function(error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    get_total_long_urls: function(successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/urls/total',
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                total_long_urls = data;
                if (successCallback) successCallback();
            },
            error: function(error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    get_user: function(successCallback) {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/user/profile',
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                user_data = data;
                if (successCallback) successCallback();
            },
            error: function(error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    refreshToken: function() {
        $.ajax({
            type: 'GET',
            data: {},
            contentType: 'application/json',
            url: '/api/v1.0/token/refresh',
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                window.localStorage.setItem("token", data.token);
                templateRenders.renderTopNavigation(data);
            },
            error: function(error) {
                templateRenders.renderAlert("alert-danger", "Oops! An error occurred: ", JSON.parse(error.responseText).message);
            }
        });
    },

    getCredentials: function(refreshCallback, successCallback) {
        $.get("/credentials", {})
            .done(function(data) {
                if (refreshCallback) refreshCallback(JSON.parse(data), successCallback);
            });
    },

    shortenUrl: function(successCallback) {
        var values = {};
        $('#shortenUrlForm :input').each(function() {
            if ($(this).val()) {
                values[this.name] = $(this).val();
            };

        });
        $.ajax({
            type: 'POST',
            data: JSON.stringify(values),
            contentType: 'application/json',
            url: '/api/v1.0/url/shorten/',
            beforeSend: functions.use_token_authentication,
            success: function(data) {
                $('#shortenUrlModal').modal('hide');
                templateRenders.renderAlert("alert-info", data["message"] + ": ", data["shorten_url"]["shorten_url_name"]);
                functions.get_total_long_urls(function() {
                    functions.get_total_shorten_urls(function() {
                        templateRenders.renderLeftAsideNavigation(total_long_urls, total_shorten_urls)
                            // if (successCallback) successCallback();
                    });
                });
            },
            error: function(error) {
                $('#shortenUrlModal').modal('hide');
                templateRenders.renderAlert("alert-danger", "", JSON.parse(error.responseText).message);
            }
        });
    }
};