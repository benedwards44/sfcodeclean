from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings

from . import models
from . import utils
from .scanner import ScanJob

import requests
import datetime
import sys
import traceback




@shared_task
def scan_code(job_id):
    """
    Do all the heavy lifting... Query the Org for all the Apex Classes and build the Symbol Table
    """

    # Load the job from the database
    job = models.Job.objects.get(pk=job_id)
    job.status = 'Processing'
    job.save()

    try:
        # Init the scan job and run
        scan_job = ScanJob(job) 
        scan_job.scan_org()

        # If the user wants the result emailed
        if job.email_result:
            utils.send_finished_email(job)

    except Exception as ex:

        job.status = 'Error'
        job.error = str(ex)
        job.stack_trace = traceback.format_exc()
        job.save()
