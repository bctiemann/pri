import datetime
import hashlib

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.urls import resolve, reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils import timezone

from users.models import SessionVisit

import logging
logger = logging.getLogger(__name__)


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings by setting a tuple of routes to ignore

    Unauthenticated views (i.e. the front site) do not have a resolved.app_name
    because they are not mapped to a namespace in the central pri/urls.py.
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

            # Exempt unauthenticated front-site views, and defer to the built-in auth for admin site
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
    """
    This middleware ensures all views within a particular resolved app (i.e. "backoffice") are protected by
    appropriate permissions. An example for backoffice is shown, where a 403 is raised if the user is not an admin.
    For apps such as customer_portal, additional logic (such as checking whether the user is an active customer)
    may need to be added.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resolved = resolve(request.path_info)
        if resolved.url_name == 'sign-out':
            return self.get_response(request)

        if request.user.is_authenticated:
            # May want to use the more granular Django permissions system instead of just allowing all is_admin
            if resolved.app_name == 'backoffice' and not request.user.is_backoffice:
                logger.info(f'{request.user} not authorized for backoffice.')
                raise PermissionDenied

        return self.get_response(request)


class RemoteHostMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Resolve the remote_ip and remote_host and store in session for tracking and reflection in templates
        request.remote_ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR')
        request.remote_host = request.META.get('REMOTE_HOST') or request.remote_ip
        request.session['remote_ip'] = request.remote_ip
        request.session['user_agent_hash'] = hashlib.md5(request.META.get('HTTP_USER_AGENT').encode('utf-8')).hexdigest()
        request.session['last_access'] = timezone.now().isoformat()

        # If this session has not visited in the past hour, record a SessionVisit
        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)
        visited_within_hour = SessionVisit.objects.filter(
            session__session_key=request.session.session_key,
            visited_at__gte=one_hour_ago,
        )
        if not visited_within_hour.exists():
            session = Session.objects.get(session_key=request.session.session_key)
            SessionVisit.objects.create(session=session)
