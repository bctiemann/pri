from django.contrib import admin
from django.urls import path, reverse_lazy
from django.conf.urls import static
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import RedirectView

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

    path('payments/', views.PaymentsView.as_view(), name='payments'),

    path('password/', views.PasswordView.as_view(), name='password'),
    path('password/done/', views.PasswordDoneView.as_view(), name='password-done'),
]
