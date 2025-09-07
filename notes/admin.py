from django.contrib import admin

from .models import *

# Register your models here.

admin.site.site_header = "MindPad Admin"
admin.site.site_title = "MindPad Admin Portal"
admin.site.index_title = "Welcome to MindPad Admin Portal"

admin.site.register(Note)
