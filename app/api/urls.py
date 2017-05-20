from .helpers import url


urlRules = {
    "/register": {
        "view": "authentication.register",
        "methods": ["POST"]
    },
    "/token": {
        "view": "authentication.get_token",
        "methods": ["POST"]
    },
    "/token/<token>/expiration/": {
        "view": "authentication.has_token_expired",
        "methods": ["GET"]
    },
    "/token/refresh": {
        "view": "authentication.refresh_token",
        "methods": ["GET"]
    },
    "/url/shorten": {
        "view": "views.generate_shorten_url",
        "methods": ["POST"]
    },
    "/urls": {
        "view": "views.get_urls",
        "methods": ["GET"]
    },
    "/shorten-urls": {
        "view": "views.get_shorten_urls",
        "methods": ["GET"]
    },
    "/shorten-urls/popularity": {
        "view": "views.get_shorten_urls_by_popularity",
        "methods": ["GET"]
    },
    "/user/urls": {
        "view": "views.get_urls_for_particular_user",
        "methods": ["GET"]
    },
    "/user/shorten-urls": {
        "view": "views.get_short_urls_for_particular_user",
        "methods": ["GET"]
    },
    "/user/shorten-urls/total": {
        "view": "views.get_total_shorten_urls_for_particular_user",
        "methods": ["GET"]
    },
    "/user/urls/total": {
        "view": "views.get_total_urls_for_particular_user",
        "methods": ["GET"]
    },
    "/shorten-url/<int:shorten_url_id>/url": {
        "view": "views.get_long_url_with_shorten_url_id",
        "methods": ["GET"]
    },
    "/shorten-url/<shorten_url_name>/url": {
        "view": "views.get_long_url_with_shorten_url_name",
        "methods": ["GET"]
    },
    "/shorten-urls/<int:shorten_url_id>/url/update": {
        "view": "views.update_shorten_url_long_url",
        "methods": ["PUT"]
    },
    "/shorten-urls/<int:shorten_url_id>/activate": {
        "view": "views.activate_shortened_url",
        "methods": ["PUT"]
    },
    "/shorten-urls/<int:shorten_url_id>/deactivate": {
        "view": "views.deactivate_shortened_url",
        "methods": ["PUT"]
    },
    "/user/profile": {
        "view": "views.get_user_profile",
        "methods": ["GET"]
    },
    "/shorten-urls/<int:shorten_url_id>/delete": {
        "view": "views.delete_shortened_url",
        "methods": ["DELETE"]
    },
    "/shorten-urls/<int:shorten_url_id>/restore": {
        "view": "views.restore_deleted_shortened_url",
        "methods": ["PUT"]
    }

}

url(url_rules=urlRules)
