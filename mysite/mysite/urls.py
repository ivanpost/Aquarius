from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

]