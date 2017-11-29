# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.db import models

import uuid

class Job(models.Model):
    """
    Holds the details about the job run
    """

    slug = models.SlugField(blank=True, null=True)

    created_date = models.DateTimeField(db_index=True, auto_now_add=True)
    finished_date = models.DateTimeField(blank=True, null=True)

    org_id = models.CharField(max_length=18)
    username = models.CharField(max_length=80, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    email_result = models.BooleanField(default=True)

    access_token = models.CharField(max_length=255)
    instance_url = models.CharField(max_length=255)

    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('Processing', 'Processing'),
        ('Finished', 'Finished'),
        ('Error', 'Error'),
    )

    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Not Started')
    error = models.TextField(blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)

    def classes(self):
        return self.apexclass_set.all().order_by('name')

    def visualforce(self):
        return self.apexpagecomponent_set.all().order_by('name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4()
        super(Job, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('job', kwargs={'slug': self.slug})


class ApexClass(models.Model):
    """
    Holds all details about an ApexClass
    """

    job = models.ForeignKey(Job)

    class_id = models.CharField(max_length=18)
    class_member_id = models.CharField(max_length=18, blank=True, null=True)
    name = models.CharField(max_length=80)
    body = models.TextField()

    symbol_table_json = models.TextField(blank=True, null=True)

    is_referenced_externally = models.BooleanField(default=False)

    # Holds a JSON structure of all the external classes that call this class
    referenced_by_json = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class ApexPageComponent(models.Model):
    """
    Hold details about an ApexPage
    """

    job = models.ForeignKey(Job)

    sf_id = models.CharField(max_length=18)
    name = models.CharField(max_length=80)
    body = models.TextField()

    TYPE_CHOICES = (
        ('Page', 'Page'),
        ('Component', 'Component'),
    )

    type = models.CharField(max_length=10, default='Page')

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

