from django.utils import translation


class ContentLanguageMiddleware:
    """Tell the browser which language the response was rendered in."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["Content-Language"] = translation.get_language() or "uk"
        return response
