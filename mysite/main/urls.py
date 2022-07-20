from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reports/', views.reports, name='reports'),
    path('controllers/<str:prefix>', views.controller, name='controller'),
    path('controllers/<str:prefix>/channels/<str:chn>', views.channel, name='channel'),
    path('controllers/<str:prefix>/channels/<str:chn>/manual_activation', views.manual_activation, name='manual_activation'),
    path('controllers/<str:prefix>/channels/<str:chn>/manual_activation/<int:minutes>', lambda r, prefix, chn, minutes: views.manual_activation(r, prefix, chn, minutes), name='manual_activation'),
    #path('controllers/<str:prefix>/<str:day>', views.controller_day, name='controller_day'),
    path('controllers/<str:prefix>/manual_activation_selector', views.manual_activation_selector,
         name="manual_activation_selector"),
    path('controllers/<str:prefix>/manual_activation_selector/turn_off_all', lambda r, prefix: views.manual_activation_selector(r, prefix, True),
         name="turn_off_all_channels"),
]