# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from . import models

class ApexClassInline(admin.TabularInline):

    fields = ['class_id', 'class_member_id','name',]
    model = models.ApexClass
    extra = 0

# Register your models here.
@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):

    list_display = ['slug', 'created_date', 'username', 'status']
    inlines = [ApexClassInline]