from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reports/', views.reports, name='reports'),
    path('controllers/<str:mqtt_user>', views.controller, name='controller'),
    path('controllers/<str:mqtt_user>/pause', views.pause, name='pause'),
    path('controllers/<str:mqtt_user>/channel_naming', views.channel_naming, name='channel_naming'),
    path('controllers/<str:mqtt_user>/pause/<int:minutes>', views.pause, name='pause'),
    path('controllers/<str:mqtt_user>/pump', views.pump, name='pump'),
    path('controllers/<str:mqtt_user>/channels/<str:chn>', views.channel, name='channel'),
    path('controllers/<str:mqtt_user>/channels/<str:chn>/create_program', lambda r, mqtt_user, chn: views.channel(r, mqtt_user, chn, True), name='create_program'),
    path('controllers/<str:mqtt_user>/channels/<str:chn>/programs/<str:prg_num>', views.program, name='program'),
    path('controllers/<str:mqtt_user>/channels/<str:chn>/manual_activation', views.manual_activation, name='manual_activation'),
    path('controllers/<str:mqtt_user>/channels/<str:chn>/manual_activation/<int:minutes>', views.manual_activation, name='manual_activation'),
    path('controllers/<str:mqtt_user>/manual_activation_selector', views.manual_activation_selector,
         name="manual_activation_selector"),
    path('controllers/<str:mqtt_user>/manual_activation_selector/turn_off_all', lambda r, mqtt_user: views.manual_activation_selector(r, mqtt_user, True),
         name="turn_off_all_channels"),
]