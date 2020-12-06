from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.urls import resolve, reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

import logging
logger = logging.getLogger(__name__)


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings by setting a tuple of routes to ignore
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), """
        The Login Required middleware needs to be after AuthenticationMiddleware.
        Also make sure to include the template context_processor:
        'django.contrib.auth.context_processors.auth'."""

        if not request.user.is_authenticated:
            resolved = resolve(request.path_info)
            current_route_name = resolved.url_name
            logger.info(f'{current_route_name} {resolved.app_name}')

            if not resolved.app_name or resolved.app_name == 'admin':
                return None

            if current_route_name not in settings.AUTH_EXEMPT_ROUTES:
                if resolved.app_name == 'api':
                    logger.info('redirecting to login from api')
                    return HttpResponseRedirect(reverse('login'))
                if resolved.app_name:
                    logger.info(f'redirecting to login from {resolved.app_name}')
                    return HttpResponseRedirect(reverse(f'{resolved.app_name}:login'))
                logger.info('redirecting to login with no app_name')
                return HttpResponseRedirect(reverse('login'))


class PermissionsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resolved = resolve(request.path_info)
        if resolved.url_name == 'sign-out':
            return self.get_response(request)

        if request.user.is_authenticated:
            if resolved.app_name == 'backoffice' and not request.user.is_admin:
                logger.info(f'{request.user} not authorized for backoffice.')
                raise PermissionDenied

        return self.get_response(request)
