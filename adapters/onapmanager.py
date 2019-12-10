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

from logger import TangoLogger

LOG = TangoLogger.getLogger("onapmanager", log_level=logging.DEBUG, log_json=True)

LOG.setLevel(logging.DEBUG)

class OnapManager:

    def __init__(self, authmanager):
        
        logging.getLogger().setLevel(logging.DEBUG)
        self.authmanager = authmanager
        LOG.info("OnapManagerConstructor")
        
    #UNUSED    
    def getVnVONAPServiceId(self,name,vendor,version):    
        LOG.info("get vnv onap service id starts")
        uuid = None
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
                 
        #url = 'http://pre-int-vnv-bcn.5gtango.eu:32002/api/v3/services'  
        url = 'http://tng-sec-gtw/api/v3/services'  
        response = requests.get(url,headers=JSON_CONTENT_HEADER)
        LOG.debug(response)
        response_json = response.content
        jjson = json.loads(response_json)
        for x in jjson:
            LOG.debug(x)            
            try:
                osm_name = x['nsd']['nsd:nsd-catalog']['nsd']['name']
                LOG.debug("osm_name: {}".format(osm_name))
                LOG.debug("ONAP service descriptor, checking if is the one we are searching:") 
                if ( x['nsd']['nsd:nsd-catalog']['nsd']['name'] == name and x['nsd']['nsd:nsd-catalog']['nsd']['vendor'] == vendor and x['nsd']['nsd:nsd-catalog']['nsd']['version'] == version ) :
                    uuid = x['uuid']
                    LOG.debug("uuid: {}".format(uuid))
            except:
                LOG.debug("this descriptor is not an ONAP one")       

        LOG.debug(uuid)
        return uuid    

    #UNUSED
    def getSPONAPServiceId(self,name,vendor,version):        
        LOG.info("get sp onap service id starts")
        uuid = None
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}          
        return uuid

    #UNUSED
    def getONAPInstance(self,instance_id,service_name):        
        LOG.info("get onap instance object starts")
        uuid = None
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        url = self.authmanager.db_host + ':8443/nbi/api/v3/service/'    
        url = url + instance_id + '/'
        url = url + '?relatedParty.id='
        url = url + self.authmanager.db_username
        url = url + '&serviceSpecification.name='
        url = url + service_name
        response = requests.get(url,headers=JSON_CONTENT_HEADER)
        LOG.debug("response: {}".format(response))
        return response        

    #UNUSED
    def instantiateONAP(self,externalId, service_instance_name, auto_service_id):
        
        url = self.authmanager.db_host + '/serviceOrder'
        JSON_CONTENT_HEADER = {'Content-Type':'application/json', 'Accept':'application/json'} 

        DATA = {
            "externalId": "{{" + externalId + "}}",
            "priority": "1",
            "description": "order for generic customer via Postman",
            "category": "Consumer",
            "requestedStartDate": "2018-04-26T08:33:37.299Z",
            "requestedCompletionDate": "2018-04-26T08:33:37.299Z",
            "relatedParty": [
                {
                "id": "{{" + self.authmanager.db_username + "}}",
                "role": "ONAPcustomer",
                "name": "{{" + self.authmanager.db_username + "}}"
                }
            ],
            "orderItem": [
                {
                "id": "1",
                "action": "add",
                "service": {
                    "name": "{{" + service_instance_name + "}}",
                    "serviceState": "active",
                    "serviceSpecification": {
                    "id": "{{" + auto_service_id + "}}"
                    }
                }
                }
            ]
            }        

        response = requests.post(url,data=DATA, headers=JSON_CONTENT_HEADER)
        LOG.debug("response: {}".format(response))
        return response       

    #UNUSED
    def terminateONAP(self,externalId, service_instance_name, auto_service_id):
        
        url = self.authmanager.db_host + '/serviceOrder'
        JSON_CONTENT_HEADER = {'Content-Type':'application/json', 'Accept':'application/json'} 

        DATA = {
            "externalId": "{{" + externalId + "}}",
            "priority": "1",
            "description": "ordering on generic customer via Postman",
            "category": "Consumer",
            "requestedStartDate": "2018-04-26T08:33:37.299Z",
            "requestedCompletionDate": "2018-04-26T08:33:37.299Z",
            "relatedParty": [
                {
                "id": "{{" + self.authmanager.db_username + "}}",
                "role": "ONAPcustomer",
                "name": "{{" + self.authmanager.db_username + "}}"
                }
            ],
            "orderItem": [
                {
                "id": "1",
                "action": "delete",
                "service": {
                    "id": "{{" + auto_service_instance_id + "}}",
                    "serviceState": "active",
                    "serviceSpecification": {
                    "id": "{{" + auto_service_id + "}}"
                    }
                }
                }
            ]
            }               

        response = requests.post(url,data=DATA, headers=JSON_CONTENT_HEADER)
        LOG.debug("response: {}".format(response))
        return response   
    