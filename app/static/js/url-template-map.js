/**
 * Created by koyexes on 23/04/2017.
 */

var urlTemplateMap = {
    "dashboard": function () {
        templateRenders.renderDashboard({});
    },
    "shorten-url/date-added": function () {
        var token = window.localStorage.getItem("token");
        functions.get_shorten_urls(token, function () {
            console.log(shorten_urls);
            templateRenders.renderShortenUrlContent(shorten_urls);
        });

    }

};

var renderTemplateOnRefresh = function (renderCallback) {
    var token = window.localStorage.getItem("token");
    functions.get_total_shorten_urls(token, function () {
        functions.get_total_long_urls(token, function () {
            functions.get_user(token, function () {
                templateRenders.renderLeftAsideNavigation(total_long_urls, total_shorten_urls);
                templateRenders.renderTopNavigation(Object.assign({"token":token}, user_data));
                renderCallback();
            })
        })
    })

}
$(document).ready(function (e) {
    functions.checkTokenValidity(function () {
        renderTemplateOnRefresh(urlTemplateMap[path]);
    }), functions.refreshToken
});

$("#shorten").click(function (e) {
    // e.preventDefault();
    console.log("hello");
    functions.checkTokenValidity(urlTemplateMap["shorten-url"], functions.refreshToken);
});