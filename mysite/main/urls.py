from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('reports/', views.reports, name='reports'),
    path('controllers/<str:prefix>', views.controller, name='controller')
]