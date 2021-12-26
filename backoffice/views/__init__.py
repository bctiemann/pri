from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.db.models import Q

from users.views import LoginView
from users.models import User


# Home and login/logout views

class AdminViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['admin_users'] = User.objects.filter(is_backoffice=True)
        return context


class LandingView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/landing.html'


class HomeView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/home.html'


class LoginView(LoginView):
    template_name = 'backoffice/login.html'
    home_url = reverse_lazy('backoffice:home')


class LogoutView(LogoutView):
    pass


# API view to track admin activity

class TrackActivityView(APIView):
    # AuthZ/authE are handled already in middleware; these are necessary here to provide request.user
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def post(self, request):
        request.user.admin_last_activity = parse_datetime(request.POST.get('last_activity'))
        request.user.save()
        return Response({
            'is_sleeping': request.user.is_sleeping,
        })


# Mixin for handling filtering/sorting and navigation pill states in page groups

class ListViewMixin:
    page_group = None
    is_create_view = False
    search_term = None
    search_fields = None
    default_sort = 'id'

    # Can be overridden for certain page groups that need further conditions for when to highlight the "List All" pill
    @property
    def is_unfiltered_list_view(self):
        return not self.kwargs.get('pk') and not self.is_create_view

    # Filtering and sorting occurs here; define search_fields on each page group's ListView
    def get_queryset(self):
        queryset = super().get_queryset()
        self.search_term = self.request.GET.get('query')
        if self.search_term and self.search_fields:
            or_condition = Q()
            for field in self.search_fields:
                or_condition.add(Q(**{f'{field}__icontains': self.search_term}), Q.OR)
            queryset = queryset.filter(or_condition)
        queryset = queryset.order_by(self.request.GET.get('sortby', self.default_sort))
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_unfiltered_list_view'] = self.is_unfiltered_list_view
        context['page_group'] = self.page_group
        context['is_create_view'] = self.is_create_view
        context['search_term'] = self.search_term
        context['sortby'] = self.request.GET.get('sortby', self.default_sort)
        return context
