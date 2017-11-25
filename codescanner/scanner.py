from django.conf import settings

from .models import ApexClass

import uuid
import requests
import time
import json

REST_URL = '/services/data/%d.0/' % settings.SALESFORCE_API_VERSION
TOOLING_URL = '%s/tooling/' % REST_URL


class ScanJob(object):
    """
    Holds all the logic for processing a job
    """

    job = None
    headers = {}
    tooling_url = None

    def __init__(self, job):
        """Init variables for the class"""
        self.job = job
        self.headers = {
            'Authorization': 'Bearer %s' % self.job.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.tooling_url = '%s%s' % (self.job.instance_url, settings.SALESFORCE_TOOLING_URL)


    def get_all_classes(self):
        """
        Queries all Apex Classes within an Org
        """

        classes = []
        url = '%squery/?q=SELECT+Id,Name,Body+FROM+ApexClass+WHERE+NamespacePrefix=NULL' % (self.tooling_url)
        result = requests.get(url, headers=self.headers)
        classes.extend(result.json().get('records'))

        # If there are more classes, we need to keep calling for more.
        while 'nextRecordsUrl' in result.json():
            result = requests.get(self.job.instance_url + result.json().get('nextRecordsUrl'), headers=self.headers)
            classes.extend(result.json().get('records'))
        return classes


    def get_metadata_container_id(self):
        """
        Creates the MetadataContainer used to hold the working copies of ApexClassMember
        https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/tooling_api_objects_metadatacontainer.htm?search_text=MetadataContainer
        """

        url = '%ssobjects/MetadataContainer' % (self.tooling_url)
        result = requests.post(url, headers=self.headers, json={'Name': str(uuid.uuid4())[:32]})
        return result.json().get('id')


    def create_class_member(self, metadata_container_id, apex_class):
        """
        Create a class member for the Apex Class
        """

        url = '%ssobjects/ApexClassMember' % (self.tooling_url)
        data = {
            'Body': apex_class.body,
            'ContentEntityId': apex_class.class_id,
            'MetadataContainerId': metadata_container_id
        }
        result = requests.post(url, headers=self.headers, json=data)
        return result.json().get('id')


    def create_container_request(self, metadata_container_id):
        """
        Runs the Async request to compile the code
        """
        url = '%ssobjects/ContainerAsyncRequest' % (self.tooling_url)
        data = {
            'IsCheckOnly': True,
            'MetadataContainerId': metadata_container_id
        }
        # This returns an ID, and must be re-queried until it's finishd
        result = requests.post(url, headers=self.headers, json=data)
        return result.json().get('id')


    def get_compile_status(self, compile_id):
        """
        Check the status of the compile job
        """
        url = '%ssobjects/ContainerAsyncRequest/%s' % (self.tooling_url, compile_id)
        result = requests.get(url, headers=self.headers)
        return result.json().get('State')


    def get_symbol_table_for_class(self, class_member_id):
        """
        Retrieves the symbol table for a class
        """
        url = '%ssobjects/ApexClassMember/%s' % (self.tooling_url, class_member_id)
        result = requests.get(url, headers=self.headers)
        return json.dumps(result.json().get('SymbolTable'))


    def scan_org(self):
        """
        Execute all the logic to scan the Org
        """

        # Delete any existing classes
        self.job.classes().delete()

        # Create the metadata container
        metadata_container_id = self.get_metadata_container_id()

        classes = []

        # Query for and get all classes
        for apex_class in self.get_all_classes():

            # Create the new class
            new_class = ApexClass()
            new_class.job = self.job
            new_class.class_id = apex_class.get('Id')
            new_class.name = apex_class.get('Name')
            new_class.body = apex_class.get('Body')
            new_class.save()

            # Create a ApexClassMember for the class
            new_class.class_member_id = self.create_class_member(metadata_container_id, new_class)
            new_class.save()

            classes.append(new_class)

        # Now we have created a ApexClassMember for each class, we need to "compile" all the classes
        # This runs to build the symbol table
        compile_request_id = self.create_container_request(metadata_container_id)

        # Continue to check for the compile results
        compile_complete = False
        compile_status = None
        while not compile_complete:
            time.sleep(3)
            compile_status = self.get_compile_status(compile_request_id)
            compile_complete = compile_status in ['Invalidated','Completed','Failed','Error','Aborted']
            
        if compile_status != 'Completed':
            self.job.status = 'Error'
            self.job.error = 'There was an error compiling your code. Please try again.'
            self.job.save()
            return

        # Once complete, we can now pull the SymbolTable for each ApexClass
        for apex_class in classes:
            apex_class.symbol_table_json = self.get_symbol_table_for_class(apex_class.class_member_id)
            apex_class.save()

        self.job.status = 'Finished'
        self.job.save()
            

