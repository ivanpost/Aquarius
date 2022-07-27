from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reports/', views.reports, name='reports'),
    path('controllers/<str:prefix>', views.controller, name='controller'),
    path('controllers/<str:prefix>/pause', views.pause, name='pause'),
    path('controllers/<str:prefix>/pause/<int:minutes>', views.pause, name='pause'),
    path('controllers/<str:prefix>/channels/<str:chn>', views.channel, name='channel'),
    path('controllers/<str:prefix>/channels/<str:chn>/create_program', lambda r, prefix, chn: views.channel(r, prefix, chn, True), name='create_program'),
    path('controllers/<str:prefix>/channels/<str:chn>/programs/<str:prg_num>', views.program, name='program'),
    path('controllers/<str:prefix>/channels/<str:chn>/manual_activation', views.manual_activation, name='manual_activation'),
    path('controllers/<str:prefix>/channels/<str:chn>/manual_activation/<int:minutes>', views.manual_activation, name='manual_activation'),
    #path('controllers/<str:prefix>/<str:day>', views.controller_day, name='controller_day'),
    path('controllers/<str:prefix>/manual_activation_selector', views.manual_activation_selector,
         name="manual_activation_selector"),
    path('controllers/<str:prefix>/manual_activation_selector/turn_off_all', lambda r, prefix: views.manual_activation_selector(r, prefix, True),
         name="turn_off_all_channels"),
]