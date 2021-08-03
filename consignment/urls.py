from django.contrib import admin
from django.urls import path, include
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
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<str:slug>/', views.CalendarView.as_view(), name='calendar'),
    path('proceeds/', views.ProceedsView.as_view(), name='proceeds'),
    path('proceeds/<str:slug>/', views.ProceedsView.as_view(), name='proceeds'),
    path('calendar_widget/', views.CalendarWidgetView.as_view(), name='calendar-widget'),
    path('calendar_widget/<str:slug>/', views.CalendarWidgetView.as_view(), name='calendar-widget'),
]