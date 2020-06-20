from django.http import HttpResponseRedirect, HttpResponse
from django.utils.deprecation import MiddlewareMixin

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        self.process_request(request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        print(request.user, flush=True)
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/user_login/') # or http response
        return None