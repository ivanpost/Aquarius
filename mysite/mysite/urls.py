from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),

]