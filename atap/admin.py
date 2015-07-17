from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(Tool)
admin.site.register(Input)
admin.site.register(Param)
admin.site.register(Output)
