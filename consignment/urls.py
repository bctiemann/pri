from django.contrib import admin
from django.urls import path, reverse_lazy
from django.conf.urls import static
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from fleet import views as fleet_views
from consignment import views


urlpatterns = [
    # path('', views.HomeView.as_view(), name='home'),
    path('', RedirectView.as_view(url='/special/calendar/'), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(next_page=reverse_lazy('consignment:login')), name='logout'),

    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<str:slug>/', views.CalendarView.as_view(), name='calendar'),
    path('proceeds/', views.ProceedsView.as_view(), name='proceeds'),
    path('proceeds/<str:slug>/', views.ProceedsView.as_view(), name='proceeds'),
    path('calendar_widget/', views.CalendarWidgetView.as_view(), name='calendar-widget'),
    path('calendar_widget/<str:slug>/', views.CalendarWidgetView.as_view(), name='calendar-widget'),
    path('reserve/<str:slug>/', views.ReserveView.as_view(), name='reserve'),
    path('unreserve/<int:pk>/', views.ReleaseReservationView.as_view(), name='release-reservation'),

    path('payments/history/', views.PaymentHistoryView.as_view(), name='payment-history'),
    path('payments/info/', views.PaymentInfoView.as_view(), name='payment-info'),

    path('password/', views.PasswordView.as_view(), name='password'),
    path('password/done/', views.PasswordDoneView.as_view(), name='password-done'),

    # AJAX route for requesting password reset token email
    path('recovery/password_reset/',
         views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             from_email=settings.SUPPORT_EMAIL,
             extra_email_context={
                 'site_name': settings.COMPANY_NAME
             },
         ),
         name='password_reset',
     ),

    # Emailed link to form for resetting password
    path('recovery/reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Success view for password recovery change form
    path('recovery/change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='consignment/account/password_change_done.html'),
         name='password_reset_complete'
     ),
]
