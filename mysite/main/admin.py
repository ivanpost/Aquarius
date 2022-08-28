from django.contrib import admin

from .models import Controller, Channel, Program, UserExtension

admin.site.register(Controller)
admin.site.register(Channel)
admin.site.register(Program)
admin.site.register(UserExtension)