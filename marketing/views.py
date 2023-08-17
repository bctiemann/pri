import logging
from django.conf import settings
from django.views.generic import TemplateView, FormView, CreateView, DeleteView, UpdateView, DetailView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import Customer
from fleet.models import Vehicle, VehicleMarketing, VehicleType, VehicleStatus
from marketing.models import NewsItem, SiteContent, NewsletterSubscription, SurveyResponse
from marketing.forms import NewsletterSubscribeForm, NewsletterUnsubscribeForm, SurveyResponseForm
from sales.tasks import send_email

logger = logging.getLogger(__name__)


# This mixin allows us to include the common query for cars and bikes into every view, for the nav menu
class NavMenuMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ready_vehicles'] = VehicleMarketing.objects.filter(status=VehicleStatus.READY).order_by('-weighting')
        context['cars'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.CAR)
        context['bikes'] = context['ready_vehicles'].filter(vehicle_type=VehicleType.BIKE)
        context['footer_news_items'] = NewsItem.objects.all()[0:3]
        return context


class HomeView(NavMenuMixin, TemplateView):
    template_name = 'front_site/home.html'

    # Note that get_context_data calls super() which overrides the NavMenuMixin method rather than the one defined in
    # TemplateView, because NavMenuMixin takes precedence in inheritance order. NavMenuMixin.get_context_data calls
    # super() in turn which does invoke TemplateView.get_context_data to build the initial context object.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        showcase_vehicles = context['ready_vehicles'].order_by('?')
        if not settings.BIKES_ENABLED:
            showcase_vehicles = showcase_vehicles.filter(vehicle_type=VehicleType.CAR)
        context['showcase_vehicle'] = showcase_vehicles.first()
        return context


class FleetView(NavMenuMixin, TemplateView):
    template_name = 'front_site/fleet.html'
    vehicle_type = None

    # If this view is called with a vehicle_type param, we validate that it is an acceptable value, then pass it
    # through to the super() method. If there is no vehicle_type, it is None by default.
    def get(self, request, *args, vehicle_type=None, **kwargs):
        vehicle_type = vehicle_type or self.vehicle_type
        if vehicle_type and vehicle_type not in ['cars', 'bikes']:
            raise Http404
        if vehicle_type == 'bikes' and not settings.BIKES_ENABLED:
            raise Http404
        return super().get(request, *args, vehicle_type=vehicle_type, **kwargs)

    def get_context_data(self, vehicle_type=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vehicles'] = context['ready_vehicles']
        if vehicle_type:
            context['vehicles'] = context.get(vehicle_type)
        context['vehicle_type'] = vehicle_type
        return context


class VehicleView(NavMenuMixin, TemplateView):
    template_name = 'front_site/vehicle.html'

    def get(self, *args, **kwargs):
        logger.debug(kwargs)
        return super().get(*args, **kwargs)

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # We filter() rather than get() because vehicle_marketing.slug is not unique (we may have multiple of the
        # same vehicle)
        context['vehicle'] = VehicleMarketing.objects.ready().filter(slug__iexact=slug).first()
        if not context['vehicle']:
            raise Http404
        return context


class ServicesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/services.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = SiteContent.objects.get(page='services')
        context['content'] = site_content.content
        return context


class SpecialsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/specials.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = SiteContent.objects.get(page='specials')
        context['content'] = site_content.content
        return context


class AboutView(NavMenuMixin, TemplateView):
    template_name = 'front_site/about.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = SiteContent.objects.get(page='about')
        context['content'] = site_content.content
        return context


class PoliciesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/policies.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = SiteContent.objects.get(page='policies')
        context['content'] = site_content.content
        return context


class NewsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/news.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        if slug:
            context['news_items'] = NewsItem.objects.filter(
                slug=self.kwargs.get('slug'),
                created_at__year=self.kwargs['year'],
                created_at__month=self.kwargs['month'],
                created_at__day=self.kwargs['day'],
            )
        else:
            context['news_items'] = NewsItem.objects.all()[0:10]
        return context


class ContactView(NavMenuMixin, TemplateView):
    template_name = 'front_site/contact.html'

    def get_context_data(self, slug=None, **kwargs):
        context = super().get_context_data(**kwargs)
        site_content = SiteContent.objects.get(page='contact')
        context['content'] = site_content.content
        return context


class TermsConditionsView(NavMenuMixin, TemplateView):
    template_name = 'front_site/terms.html'


class PrivacyPolicyView(NavMenuMixin, TemplateView):
    template_name = 'front_site/privacy.html'


class MediaInquiriesView(NavMenuMixin, TemplateView):
    template_name = 'front_site/media.html'


# Newsletter subscribe/unsubscribe views
# These also handle no-JS functionality of form POSTs

class NewsletterView(NavMenuMixin, FormView):
    template_name = 'front_site/newsletter/subscribe.html'
    form_class = NewsletterSubscribeForm

    def form_valid(self, form):
        result = super().form_valid(form)

        # TODO: Save email on session as "newsletter_email" or some such, for user tracking/analytics

        return result

    # def get_context_data(self, slug=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
    #     return context

    # If form is submitted without JS, just push to the success page as a honeypot
    def get_success_url(self):
        return reverse('newsletter-done')


class NewsletterDoneView(NavMenuMixin, TemplateView):
    template_name = 'front_site/newsletter/subscribe_done.html'

    # def get_context_data(self, slug=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['recaptcha_site_key'] = settings.RECAPTCHA_SITE_KEY
    #     return context


class NewsletterSubscribeConfirmView(NavMenuMixin, DetailView):
    template_name = 'front_site/newsletter/subscribe_confirm.html'
    model = NewsletterSubscription

    def get_object(self):
        return get_object_or_404(self.get_queryset(), hash=self.kwargs['hash'])

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.is_confirmed:
            self.object.confirmed_at = timezone.now()
            self.object.save()

            email_subject = 'Performance Rentals Newsletter Confirmed'
            email_context = {
                'subscription': self.object,
                'site_url': settings.SERVER_BASE_URL,
            }
            send_email(
                [self.object.email], email_subject, email_context,
                text_template='front_site/email/newsletter_subscribe_confirmed.txt',
                html_template='front_site/email/newsletter_subscribe_confirmed.html'
            )
        return response


# For non-JS flow. JS flow is in api.views.ValidateNewsletterUnsubscriptionView
class NewsletterUnsubscribeView(NavMenuMixin, FormView):
    template_name = 'front_site/newsletter/unsubscribe.html'
    form_class = NewsletterUnsubscribeForm

    def form_valid(self, form):
        result = super().form_valid(form)
        subscriptions = NewsletterSubscription.objects.filter(email=form.cleaned_data['email'])
        subscriptions.delete()
        return result

    def get_success_url(self):
        return reverse('newsletter-unsubscribe-done')


class NewsletterUnsubscribeDoneView(NavMenuMixin, TemplateView):
    template_name = 'front_site/newsletter/unsubscribe_done.html'


# Survey views (unique link emailed to a recent customer for a followup; see Customer.send_survey_email)

class SurveyView(NavMenuMixin, UpdateView):
    template_name = 'front_site/survey/survey.html'
    model = SurveyResponse
    form_class = SurveyResponseForm

    # get_object resolves to a Customer, but the form will be manually bound to a SurveyResponse object and saved
    # in a customized form_valid rather than updating the Customer
    def get_object(self, queryset=None):
        email = Customer.survey_tag_to_email(self.kwargs['tag'])
        if not email:
            raise Http404
        return Customer.objects.get(user__email=email)

    def form_valid(self, form):
        survey_response = self.model.objects.create(**form.cleaned_data)
        survey_response.customer = self.object
        survey_response.save()
        self.object.survey_done = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('survey-done', kwargs={'tag': self.object.survey_tag})


class SurveyDoneView(NavMenuMixin, TemplateView):
    template_name = 'front_site/survey/done.html'
