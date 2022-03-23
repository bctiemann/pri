from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication

from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.views import LogoutView
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import FieldError

from users.views import LoginView
from users.models import User
from backoffice.models import BBSPost
from fleet.models import VehicleMarketing, VehicleStatus
from sales.models import Reservation, Rental, PerformanceExperience, JoyRide, GiftCertificate, AdHocPayment
from service.models import ScheduledService, Damage


# Home and login/logout views

class AdminViewMixin:

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['admin_users'] = User.objects.filter(is_backoffice=True)
        context['now'] = timezone.now()
        context['vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('vehicle_type', 'id')

        context['todo_list_rentals'] = Rental.objects.filter(status__in=(
            Rental.Status.INCOMPLETE,
            Rental.Status.CONFIRMED,
            Rental.Status.IN_PROGRESS,
            Rental.Status.COMPLETE,
        )).select_related('customer')

        context['reservations'] = Reservation.objects.filter(status=Reservation.Status.UNCONFIRMED)
        context['rentals'] = Rental.objects.filter(status__in=(
            Rental.Status.INCOMPLETE,
            Rental.Status.CONFIRMED,
            Rental.Status.IN_PROGRESS,
        ))
        context['performance_experiences'] = PerformanceExperience.objects.filter(status=PerformanceExperience.Status.PENDING)
        context['joy_rides'] = JoyRide.objects.filter(status=JoyRide.Status.PENDING)
        context['maintenances'] = ScheduledService.objects.filter(is_due=True)
        context['damages'] = Damage.objects.filter(is_repaired=False)
        context['gift_certificates'] = GiftCertificate.objects.filter(is_paid=False)
        context['adhoc_payments'] = AdHocPayment.objects.filter(is_paid=False, is_submitted=True)
        return context


class LandingView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/landing.html'


class HomeView(AdminViewMixin, TemplateView):
    template_name = 'backoffice/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        three_days_ago = timezone.now() - timedelta(days=3)
        context['bbs_posts'] = BBSPost.objects.filter(created_at__gte=three_days_ago, deleted_at__isnull=True)
        context['short_bbs'] = True
        return context


class HomeAddPostView(AdminViewMixin, CreateView):
    template_name = 'backoffice/home/add_post.html'
    model = BBSPost
    fields = ('body',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        post.reply_to = post
        post.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:home')


class HomeEditPostView(AdminViewMixin, UpdateView):
    template_name = 'backoffice/home/edit_post.html'
    model = BBSPost
    fields = ('body',)

    def get_object(self, queryset=None):
        queryset = self.get_queryset().filter(author=self.request.user)
        return super().get_object(queryset)

    def get_success_url(self):
        return reverse('backoffice:home')


class HomeReplyPostView(AdminViewMixin, CreateView):
    template_name = 'backoffice/home/reply_post.html'
    model = BBSPost
    fields = ('body',)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.reply_to = self.get_reply_post()
        post.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_reply_post(self):
        try:
            return BBSPost.objects.filter(reply_to=self.kwargs['pk']).first()
        except:
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        parent_post = self.get_reply_post()
        context['bbspost'] = parent_post
        context['thread_posts'] = BBSPost.objects.filter(reply_to=parent_post)
        return context

    def get_success_url(self):
        return reverse('backoffice:home')


class HomeDeletePostView(AdminViewMixin, UpdateView):
    template_name = 'backoffice/home/delete_post.html'
    model = BBSPost
    fields = ()

    def form_valid(self, form):
        self.object.deleted_at = timezone.now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('backoffice:home')


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
        is_sleeping = False
        if request.user.is_authenticated:
            request.user.admin_last_activity = parse_datetime(request.POST.get('last_activity'))
            request.user.save()
            is_sleeping = request.user.is_sleeping
        return Response({
            'is_sleeping': is_sleeping,
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
        sort_field = self.request.GET.get('sortby', self.default_sort)
        try:
            queryset = queryset.order_by(sort_field)
        except FieldError:
            pass
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_unfiltered_list_view'] = self.is_unfiltered_list_view
        context['page_group'] = self.page_group
        context['is_create_view'] = self.is_create_view
        context['search_term'] = self.search_term
        context['sortby'] = self.request.GET.get('sortby', self.default_sort)
        return context
