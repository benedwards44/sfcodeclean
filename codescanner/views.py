# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views import View
from django.urls import reverse

from . import models
from . import forms
from . import utils
from .tasks import scan_code

import requests
import urllib
import json



class IndexView(FormView):
    """
    Home page
    """

    form_class = forms.LoginForm
    template_name = 'index.html'

    def _get_auth_url(self, environment):
        """
        Get the Salesforce auth URL
        """

        # Build the URL to direct to
        sub_domain = utils.get_subdomain(environment)
        url = 'https://%s.salesforce.com/services/oauth2/authorize?response_type=code&client_id=%s&redirect_uri=%s&state=%s' % (
            sub_domain, settings.SALESFORCE_CONSUMER_KEY, urllib.quote_plus(settings.SALESFORCE_REDIRECT_URI), environment)
        return url

    def get_success_url(self):
        """
        Redirect to the approach Salesforce auth page
        """
        return self._get_auth_url(self.request.POST['environment'])


class AuthCallbackView(CreateView):
    """
    Handle the OAuth callback from Salesforce
    """

    fields = ['org_id','access_token','instance_url','username','email','email_result','error']
    model = models.Job
    template_name = 'callback.html'


    def _get_token_url(self, org_type):
        """
        Get the token URL
        """
        sub_domain = utils.get_subdomain(org_type)
        url = 'https://%s.salesforce.com/services/oauth2/token' % sub_domain
        return url


    def _get_data_payload(self, oauth_code):
        """
        Build the data payload dict
        """
        return {
            'grant_type':'authorization_code',
            'client_id': settings.SALESFORCE_CONSUMER_KEY,
            'client_secret':settings.SALESFORCE_CONSUMER_SECRET,
            'redirect_uri': settings.SALESFORCE_REDIRECT_URI,
            'code': oauth_code
        }


    def get_initial(self, *args, **kwargs):
        """
        Load initial values for the form
        """
        
        # Get the oauth values
        oauth_code = self.request.GET.get('code')
        org_type = self.request.GET.get('state')

        url = self._get_token_url(org_type)
        data = self._get_data_payload(oauth_code)

        # Attempt the login
        response = requests.post(url, headers={'Content-Type':'application/x-www-form-urlencoded'}, data=data)

        # Load json to python dict
        response = response.json()

        # If error, return the error to the user
        if 'error_description' in response:
            return {
                'error': response.get('error_description')
            }
        else:

            # Load the IDs from the response
            user_id = response['id'][-18:]
            org_id = response['id'][:-19]
            org_id = org_id[-18:]

            access_token = response.get('access_token')
            instance_url = response.get('instance_url')

            # Get the SF user details
            user = utils.get_user(instance_url, access_token, user_id)

            # Return the values loaded in the form
            # This gives a chance for the user to confirm the Org they want to run the logic on
            return {
                'org_id': org_id,
                'access_token': access_token,
                'instance_url': instance_url,
                'username': user.get('Username'),
                'email': user.get('Email')
            }
        """
        return {
            'org_id': '123',
            'access_token': '123',
            'instance_url': '123',
            'username': 'ben@edwards.nz',
            'email': 'ben@edwards.nz'
        }
        """

class JobProcessingView(DetailView):
    """
    The loading page to display while the job processes
    """
    model = models.Job
    template_name = 'scanning.html'

    def get(self, request, *args, **kwargs):

        # Start the job if it hasn't already been started
        job = self.get_object()
        if job.status == 'Not Started':
            # Run the job
            scan_code.delay(job.id)

        return super(JobProcessingView, self).get(request, *args, **kwargs)


class JobStatusView(View):
    """
    Return the status of the job
    """
    
    def get(self, request, *args, **kwargs):
        """
        Return the status of the Job in JSON
        """
        job = get_object_or_404(models.Job, slug=self.kwargs.get('slug'))

        return JsonResponse({
            'status': job.status,
            'error': job.error
        })



class JobView(DetailView):
    """
    The job to display
    """ 

    context_object_name = 'job'
    model = models.Job
    template_name = 'job.html'

    # If the job hasn't started or is processing, display the loading page
    def dispatch(self, *args, **kwargs):

        job = self.get_object()

        # If not started or processing, go to the processing page
        if job.status in ['Not Started', 'Processing']:
            return HttpResponseRedirect(reverse('job-scanning', kwargs={'slug': job.slug}))

        # Else return the job
        return super(JobView, self).dispatch(*args, **kwargs)



class JobJsonView(View):
    """
    Return the JSON details of a job
    """
    
    def get(self, request, *args, **kwargs):
        """
        Return the status of the Job in JSON
        """
        job = get_object_or_404(models.Job, slug=self.kwargs.get('slug'))

        response = []

        for apex_class in job.classes():
            response.append({
                'Id': apex_class.class_id,
                'Name': apex_class.name,
                'SymbolTable': json.loads(apex_class.symbol_table_json)
            }) 

        return JsonResponse(response, safe=False)