/**
 * Created by koyexes on 23/04/2017.
 */
var templateRenders = {
    renderLeftAsideNavigation: function(total_long_urls, total_shorten_urls) {
        $.post("/render_left_aside_navigation/", JSON.stringify(Object.assign(total_long_urls, total_shorten_urls)))
            .done(function(data) {
                $("#left-aside-nav").empty().append(data);
            });
    },
    renderAlert: function(alertType, headline, message) {
        var alertTemplate = '<div class="alert ' + alertType + ' alert-dismissible" role="alert"> ' + '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' + '<span aria-hidden="true">&times;</span></button> ' + '<strong>' + headline + '</strong> ' + message + '</div>';
        $("#alert").empty().append(alertTemplate);

    },
    renderTopNavigation: function(data) {
        $.post("/render_top_navigation/", JSON.stringify(data))
            .done(function(data) {
                $("header").empty().append(data);
            });
    },
    renderDashboard: function(data) {
        $.post("/render_dashboard/", JSON.stringify(data))
            .done(function(data) {
                $("#content").empty().append(data);
            });
    },
    renderShortenUrlContent: function(data) {
        $.post("/render_shorten_url_content/", JSON.stringify(data))
            .done(function(data) {
                $("#content").empty().append(data);
            });
    }
};