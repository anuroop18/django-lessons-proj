from django.conf import settings


def static_bundle_url(request):
    """
    Static resources are deployed separately (i.e. not from django app)
    and are available via /static/ prefix.

    In production static resources are versioned.
    """
    if settings.DEBUG:
        static_js = "/static/js/bundle.js"
        static_css = "/static/css/bundle.css"
    else:
        static_ver = settings.STATIC_ASSETS_VER
        static_js = f"/static/js/all.{static_ver}.js"
        static_css = f"/static/css/all.{static_ver}.css"
    return {
        'STATIC_JS_URL': static_js,
        'STATIC_CSS_URL': static_css,
    }
