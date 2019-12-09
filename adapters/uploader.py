#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import os, sys, logging, uuid, json
#from werkzeug import secure_filename

#import serviceplatform
import psycopg2
import requests
import subprocess
import models.database as database
import re
import ast
from ast import literal_eval
import yaml
import time
from threading import Thread
import threading 
from _thread import start_new_thread
import _thread
import logging

from flask import Flask, request, jsonify, render_template
import os, sys, logging, json, argparse 
from configparser import ConfigParser
import requests
import psycopg2

from osmclient import client as osmclient
from osmclient.common.exceptions import ClientException

from logger import TangoLogger

LOG = TangoLogger.getLogger("uploader", log_level=logging.DEBUG, log_json=True)

LOG.setLevel(logging.DEBUG)
#LOG.info("Hello world.")

class Uploader:

    def __init__(self, db_type, db_host):
        
        logging.getLogger().setLevel(logging.DEBUG)
        self.db_type = db_type
        self.db_host = db_host
        LOG.info("UploaderConstructor")
     
    def uploadPackage(self,package):
        LOG.info("upload package starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.db_type == 'sonata':               
            url = self.db_host + ':32002/api/v3/packages'
            
            files = {'package': open(package,'rb')}
            upload = requests.post(url, files=files)
            LOG.debug("upload: {}".format(upload.text))
            return upload.text

        if self.db_type == 'onap':               
            url = self.db_host + '/sdc/v1/catalog/services/{uuid}/resourceInstances/{resourceInstanceNormalizedName}/artifacts'            
            files = {'package': open(package,'rb')}
            upload = requests.post(url, files=files)
            if request.method == 'POST':
                return upload.text

    def uploadOSMService(self,request):  
        LOG.info("upload osm service starts")
        if self.db_type == 'osm':               
            token = self.getOSMToken(request)
            #file_to_upload = content['service']
            file_to_upload = request
            file_composed = "@" + file_to_upload
            file = {'nsd-create': open(file_to_upload, 'rb')}           
            data = {'service':file_to_upload}

            HEADERS = {
                'Accept':'application/yaml',
                'Content-Type':'application/zip', 
                'Authorization':'Bearer ' +token+''                
            }
            url = self.db_host + ':9999/osm/nsd/v1/ns_descriptors_content'            
            url_2 = url.replace("http","https")
        
            upload_nsd = "curl -s -X POST --insecure -H \"Content-type: application/yaml\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            upload_nsd_2 = upload_nsd +token + "\" "
            upload_nsd_3 = upload_nsd_2 + " --data-binary "
            upload_nsd_4 = upload_nsd_3 + "\"@" +file_to_upload+ "\" " + url_2

            LOG.debug("upload: {}".format(upload_nsd_4))
            upload = subprocess.check_output([upload_nsd_4], shell=True)
            try:
                callback_url = content['callback']
                LOG.debug("Callback url specified")
                _thread.start_new_thread(self.OSMUploadServiceCallback, (token,url_2,callback_url,upload))
            except:
                LOG.debug("No callback url specified")

            LOG.debug("resp_upload: {}".format(upload))
            return (upload)  
    
    def uploadPackageStatus(self,process_uuid):

        status = None
        LOG.info("uploadPackageStatusstarts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        url = self.db_host + ':32002/api/v3/packages/status/' + process_uuid            
        LOG.info(process_uuid)
        LOG.info(url)           
        try:
            upload_status_curl = requests.get(url, headers=JSON_CONTENT_HEADER) 
            LOG.debug(upload_status_curl)
            LOG.debug(upload_status_curl.text)
            upload_status_curl_json = json.loads(upload_status_curl.text)        
            LOG.debug(upload_status_curl_json)
            status = upload_status_curl_json['package_process_status']
            return status
        except:
            msg = "{\"error\": \"error checking the status of the uploaded package\"}"
            return msg       
        
    def uploadPackageOnap (self,pkg_path):
        LOG.info("upload onap package starts")
                      
        user_id = self.db_username

        url = self.db_host + '8443:/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products//versions//orchestration-template-candidate'                       
        upload_pkg = "curl -s -X POST --insecure -H \"Accept: application/json\" -H \"Content-Type: application/x-www-form-urlencoded\" -H \"X-FromAppId: robot-ete\" -H \"X-TransactionId: robot-ete-ba84612d-c1c6-4c53-9967-7b1dff276c7a\" -H \"cache-control: no-cache\" -H \"content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW\" "
        upload_pkg_2 = upload_pkg + "-H \"USER_ID: \"" + user_id + " "
        upload_pkg_3 = upload_pkg_2 + " -F upload=@" + pkg_path
        
        LOG.debug(upload_pkg_3)
        upload = subprocess.check_output([upload_pkg_3], shell=True)

        '''
        try:
            callback_url = content['callback']
            LOG.debug("Callback url specified")
            _thread.start_new_thread(self.OSMUploadServiceCallback, (token,url_2,callback_url,upload))
        except:
            LOG.debug("No callback url specified")
        '''

        LOG.debug(upload)
        return (upload)     