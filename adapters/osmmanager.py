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

LOG = TangoLogger.getLogger("osmmanager", log_level=logging.DEBUG, log_json=True)

LOG.setLevel(logging.DEBUG)

class OsmManager:

    def __init__(self, authmanager):
        
        logging.getLogger().setLevel(logging.DEBUG)
        self.authmanager = authmanager
        LOG.info("OsmManagerConstructor")
    
    def getOSMServiceId(self,name,vendor,version):
        LOG.info("get OSM service id starts")
        service_id = None 
        exists = 'NO'   
        token = self.getOSMToken(request)
        LOG.debug(token)        
        url = self.authmanager.db_host + ':9999/osm/nsd/v1/ns_descriptors_content'
        url_2 = url.replace("http","https")
        LOG.debug(url_2)        
        nsds = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "
        nsds_2 = nsds +token + "\"  " + url_2 
        LOG.debug(nsds_2)
        response = None

        try:
            LOG.debug("loading descriptrs list:")
            response = subprocess.check_output([nsds_2], shell=True)
            LOG.debug(response)
        except:
            service_id = "error"
            return service_id        

        jjson = json.loads(response)
        LOG.debug(jjson)

        LOG.debug(name)
        LOG.debug(vendor)
        LOG.debug(version)

        for x in jjson:
            try:
                LOG.debug(x)
                LOG.debug(x['name'])
                LOG.debug(x['vendor'])
                LOG.debug(x['version'])
                LOG.debug(x['_id'])

                if ( x['name'] == name and x['vendor'] == vendor and x['version'] == version ):
                    LOG.debug(x['name'])
                    service_id = x['_id']
                    exists = 'YES' 
            except:
                LOG.debug("service not readeble")
        
        if service_id == None: 
            service_id = "error"

        return service_id
    
    def getOSMToken(self,request):        
        LOG.info("get osm token starts")      
        JSON_CONTENT_HEADER = {'Accept':'application/json'}   

        if self.authmanager.db_type == 'osm':
            url = self.authmanager.db_host + ':9999/osm/admin/v1/tokens'
            url2 = url.replace("http","https")
            pr_name = self.authmanager.db_project_name
            
            if pr_name:
                project_id_for_token = pr_name
            if not pr_name:
                data = request.get_json()
                project_id_for_token = data['project_id']
                LOG.debug("project name from json body:")
                LOG.debug(pr_name)


            data_for_token= "{username: \'" +self.authmanager.db_username+ "\', password: \'" +self.authmanager.db_password+ "\', project_id: \'" +project_id_for_token+ "\'}"
            get_token = requests.post(url2,data=data_for_token,headers=JSON_CONTENT_HEADER,verify=False)
            token_id = get_token.json()
            LOG.debug("token: {}".format(token_id['id']))
            return token_id['id']
        
    def deleteOSMService(self,id_to_delete):
            LOG.info("delete osm service starts")
            token = self.getOSMTokenForDelete()
            LOG.debug(token)
            url = self.authmanager.db_host + ':9999/osm/nsd/v1/ns_descriptors_content'
            url_2 = url.replace("http","https")
            delete_nsd = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/yaml\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            delete_nsd_2 = delete_nsd +token + "\"  " + url_2 + "/" + id_to_delete + " -X DELETE" 
            LOG.debug("delete_nsd: {}".format(delete_nsd_2))
            deletion = subprocess.check_output([delete_nsd_2], shell=True)
            LOG.debug("resp_delete_nsd: {}".format(deletion))
            return (deletion)

    def deleteOSMFunction(self,id_to_delete):
            LOG.info("delete osm function starts")
            token = self.getOSMTokenForDelete()
            url = self.authmanager.db_host + ':9999/osm/vnfpkgm/v1/vnf_packages'
            url_2 = url.replace("http","https")
            delete_nsd = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/yaml\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            delete_nsd_2 = delete_nsd +token + "\"  " + url_2 + "/" + id_to_delete + " -X DELETE" 
            LOG.debug("delete_osm_function: {}".format(delete_nsd_2))
            deletion = subprocess.check_output([delete_nsd_2], shell=True)
            LOG.debug("resp_delete_osm_function: {}".format(deletion))
            return (deletion)            

    def getOSMTokenForDelete(self):            
        LOG.info("get osm token for delete starts")
        JSON_CONTENT_HEADER = {'Accept':'application/json'}   

        if self.authmanager.db_type == 'osm':
            url = self.authmanager.db_host + ':9999/osm/admin/v1/tokens'
            url_2 = url.replace("http","https")
            pr_name = self.authmanager.db_project_name

            if pr_name:
                project_id_for_token = pr_name

            if not pr_name:
                project_id_for_token = self.authmanager.db_project
                LOG.debug("project name from json body:")
                LOG.debug(pr_name)

            #LOG.debug(project_id_for_token)
            admin_data = "{username: 'admin', password: 'admin', project_id: 'admin'}"
            LOG.debug("admin_data: {}".format(admin_data))
            data_for_token= "{username: \'" +self.authmanager.db_username+ "\', password: \'" +self.authmanager.db_password+ "\', project_id: \'" +project_id_for_token+ "\'}"
            get_token = requests.post(url_2,data=data_for_token,headers=JSON_CONTENT_HEADER,verify=False)
            
            token_id = get_token.json()
            LOG.debug("token: {}".format(token_id['id']))
            return token_id['id']            


    def getOSMInstaceStatus(self,service_id): 
            LOG.info("get osm instance status starts")            
            token = self.getOSMToken(service_id)
            LOG.debug(token)                 
            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances/' + service_id
            url_2 = url.replace("http","https")
            status_ns = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/yaml\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            status_ns_2 = status_ns +token + "\" "
            status_ns_3 = status_ns_2 + " " + url_2        
            LOG.debug("curl_status: {}".format(status_ns_3))
            status = subprocess.check_output([status_ns_3], shell=True)    
            LOG.debug("resp_status: {}".format(status))                    
            return (status)     

    def OSMInstantiateCallback(self, callback_url,inst_resp_yaml):
        LOG.info("osm instantiate callback starts")
        response = yaml.load(inst_resp_yaml)
        LOG.debug("inst_resp_yaml: {}".format(response))
        token = self.getOSMToken(request)
        
        url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances_content'
        url_2 = url.replace("http","https")         

        service_id = response['id']
        status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id 
        LOG.debug("status_url: {}".format(status_url))
        
        operational_status = None
        status = None 
        '''
        kwargs = {}
        osmcli = osmclient.Client(host=self.authmanager.db_host, sol005=True, **kwargs)
        resp = osmcli.ns.create(nsd_name, ns_name, self.authmanager.vim_account)
        LOG.info("osmcli_inst_dump: {}".format(yaml.safe_dump(resp)))            
        '''
        while ( operational_status != 'running' and operational_status != 'error' and operational_status != 'failed' ):               
            try:
                '''
                resp = osmcli.ns.create(nsd_name, ns_name, self.authmanager.vim_account)
                LOG.debug("osmcli_inst_dump: {}".format(yaml.safe_dump(resp)))
                '''
                status_curl = subprocess.check_output([status_url], shell=True)
                
                
                instance_json = json.loads(status_curl)
                LOG.debug("instance_json: {}".format(instance_json))
                
                operational_status = instance_json['operational-status']
                LOG.debug("operational_status: {}".format(operational_status))
                
                status = instance_json['config-status']
                LOG.debug("config-status: {}".format(status)) 
                
                detailed_status = instance_json['detailed-status']
                LOG.debug("detailed_status: {}".format(detailed_status))
                
                LOG.debug("Retraying in 3 sec")
                time.sleep(3)
                
            except:
                LOG.debug("Exception while retrying")
                
               

        callback_msg = None

        '''
        while ( config_status == 'init' ) : 
            try:
                status = data['config-status']                    
                LOG.debug(status)
            except:
                LOG.debug("Retraying in 3 sec")
                LOG.debug(status)
                time.sleep(3)
                status_curl = subprocess.check_output([status_url], shell=True)
                LOG.debug(status_curl)
                instance_json = json.loads(status_curl)
                config_status = instance_json['config-status']
                LOG.debug(config_status)
                operational_status = instance_json['operational-status']
                LOG.debug(operational_status)
                detailed_status = instance_json['detailed-status']
                LOG.debug(detailed_status)   
        '''                



        if operational_status == 'failed':
            #callback_msg = detailed_status.__str__()
            detailed_status = instance_json['detailed-status']
            LOG.debug("detailed_status: {}".format(detailed_status)) 
            callback_msg = str(detailed_status)
            callback_msg = "{\"error\": \"Error instantiating, check the logs\"}"

            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + callback_url                
            LOG.debug("callback_post: {}".format(callback_post)) 
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug("call: {}".format(call)) 


            callback_post_monitoring = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + self.authmanager.mon_url            
            LOG.debug("callback_post_monitoring: {}".format(callback_post_monitoring)) 
            call_monitoring = subprocess.check_output([callback_post_monitoring], shell=True)
            LOG.debug("call_monitoring: {}".format(call_monitoring)) 

        if operational_status == 'error':
            
            detailed_status = instance_json['detailed-status']
            LOG.debug("detailed_status: {}".format(detailed_status)) 
            callback_msg = str(detailed_status)
            callback_msg = "{\"error\": \"Error instantiating, check the logs\"}"

            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + callback_url                
            LOG.debug("callback_post: {}".format(callback_post))
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug("resp_call: {}".format(call))


            callback_post_monitoring = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + self.authmanager.mon_url            
            LOG.debug("callback_post_monitoring: {}".format(callback_post_monitoring))
            call_monitoring = subprocess.check_output([callback_post_monitoring], shell=True)
            LOG.debug("call_monitoring: {}".format(call_monitoring))        

        #if operational_status == 'running':             
        if ( operational_status == 'running' and config_status == 'configured' ) :             
            LOG.debug("RUNNING/CONFIGURED NS")
            status = config_status
            LOG.debug("status: {}".format(status)) 
            callback_msg = self.instantiationInfoCurator(service_id)
            LOG.debug("callback_msg: {}".format(callback_msg)) 

            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + callback_url
            LOG.debug("callback_post: {}".format(callback_post)) 
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug("call: {}".format(call)) 

            #Monitoring callback       
            callback_msg = self.instantiationInfoMonitoring(service_id)
            callback_post_monitoring = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + self.authmanager.mon_url
            LOG.debug("callback_post_monitoring: {}".format(callback_post_monitoring)) 
            call_monitoring = subprocess.check_output([callback_post_monitoring], shell=True)
            LOG.debug("call_monitoring: {}".format(call_monitoring))
        
        LOG.debug("callback ends")            

        '''
        status = config_status
        LOG.debug(status)
        #callback_msg='{\"Message\":\"The service ' + service_id + ' is in status: ' + status + '\"}'
        callback_msg = self.instantiationInfoCurator(service_id)
        LOG.debug(callback_msg)
        
        #callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + str(callback_msg) + "'" + " " + callback_url
        callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + callback_url
        LOG.debug(callback_post)
        call = subprocess.check_output([callback_post], shell=True)
        LOG.debug(call)

        #Monitoring callback       
        callback_msg = self.instantiationInfoMonitoring(service_id)
        callback_url_monitoring = self.getMonitoringURLs()
        callback_post_monitoring = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + callback_msg + "'" + " " + callback_url_monitoring
        LOG.debug(callback_post_monitoring)
        call_monitoring = subprocess.check_output([callback_post_monitoring], shell=True)
        LOG.debug(call_monitoring)
        LOG.debug("callback ends")
        '''

    def OSMTerminateStatus(self,url_2,ns_id):
        LOG.info("osm terminate status starts")        
        service_id = ns_id
        token = self.getOSMToken(ns_id)
        status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
        LOG.debug("status_url: {}".format(status_url))
        status_curl = subprocess.check_output([status_url], shell=True)
        LOG.debug("status_curl: {}".format(status_curl))
        with open('/app/temp.file') as f:
            data = json.load(f)

        status = 'my_status'
        is_active = 'not'

        while status != '404':    
            while is_active == 'not':
                try:
                    status = data['admin']['deployed']['RO']['nsr_status'] 
                    is_active = 'yes'
                    status = '404'
                except:
                    is_active = 'not'
                    status = 'my_status'
                    LOG.debug("Retraying in 3 sec")
                    time.sleep(3)
                    status_curl = subprocess.check_output([status_url], shell=True)
                    LOG.debug("status_curl: {}".format(status_curl))
                    with open('/app/temp.file') as f:
                        data = json.load(f)

        status = "terminated"  
        return status

    #UNUSED
    def OSMTerminateCallback(self,token,url_2,callback_url,ns_id):
        LOG.info("osm terminate callback starts")
        service_id = ns_id
        status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
        LOG.debug("status_url: {}".format(status_url))
        status_curl = subprocess.check_output([status_url], shell=True)
        LOG.debug("status_curl: {}".format(status_url))
        with open('/app/temp.file') as f:
            data = json.load(f)

        status = 'my_status'
        is_active = 'not'

        while status != '404':    
            while is_active == 'not':
                try:
                    status = data['admin']['deployed']['RO']['nsr_status'] 
                    is_active = 'yes'
                    status = '404'
                except:
                    is_active = 'not'
                    status = 'my_status'
                    LOG.debug("Retraying in 3 sec")
                    time.sleep(3)
                    status_curl = subprocess.check_output([status_url], shell=True)
                    LOG.debug("status_curl: {}".format(status_url))
                    with open('/app/temp.file') as f:
                        data = json.load(f)
                                         
        LOG.debug("status: {}".format(status))
        callback_msg='{\"Message\":\"The service ' + service_id + ' was terminated\"}'
        LOG.debug("callback_msg: {}".format(callback_msg))
        callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + str(callback_msg) + "'" + " " + callback_url
        call = subprocess.check_output([callback_post], shell=True)
        LOG.debug("call: {}".format(call))
        LOG.debug("callback end")        

    #UNUSED
    def OSMUploadFunctionCallback(self,token,url_2,callback_url,inst_resp_yaml):
        LOG.info("osm upload function callback starts")                        
        response = yaml.load(inst_resp_yaml)
        service_id = response['id']
        status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
        LOG.debug("status_url: {}".format(status_url))
        status_curl = subprocess.check_output([status_url], shell=True)
        LOG.debug("status_curl: {}".format(status_curl))

        with open('/app/temp.file') as f:
            data = json.load(f)

        LOG.debug("data: {}".format(data))
        status = 'my_status'

        while status == 'my_status':                            
            status = data['_admin']['onboardingState']
            if status != 'ONBOARDED':
                LOG.debug("Retrying in 3 sec")
                LOG.debug(status)
                time.sleep(3)
                status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
                LOG.debug(status_url)            
                status_curl = subprocess.check_output([status_url], shell=True)
                LOG.debug(status_curl)
                with open('/app/temp.file') as f:
                    data = json.load(f)
                    LOG.debug("data: {}".format(data))
     
        callback_msg='{\"Message\":\"The function descriptor ' + service_id + ' is in status: ' + status + '\"}'
        LOG.debug("callback_msg: {}".format(callback_msg))
        callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + str(callback_msg) + "'" + " " + callback_url
        LOG.debug("callback_post: {}".format(callback_post))
        call = subprocess.check_output([callback_post], shell=True)
        LOG.debug("call: {}".format(call))
        LOG.debug("callback end")        

    def OSMUploadServiceCallback(self,token,url_2,callback_url,inst_resp_yaml):
        LOG.info("osm upload service callback starts")                      
        response = yaml.load(inst_resp_yaml)
        service_id = response['id']
        status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
        LOG.debug("status_url: {}".format(status_url))
        status_curl = subprocess.check_output([status_url], shell=True)
        LOG.debug("status_curl: {}".format(status_curl))
        with open('/app/temp.file') as f:
            data = json.load(f)
        LOG.debug("data: {}".format(data))
        status = 'my_status'

        while status == 'my_status': 
            status = data['_admin']['onboardingState']
            if status != 'ONBOARDED':
                LOG.debug("Retrying in 3 sec")
                time.sleep(3)
                status_url = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer " + token + "\" " + url_2 + "/" + service_id + " > /app/temp.file"
                LOG.debug("status_url: {}".format(status_url))          
                status_curl = subprocess.check_output([status_url], shell=True)
                LOG.debug("status_curl: {}".format(status_curl)) 
                with open('/app/temp.file') as f:
                    data = json.load(f)
                    LOG.debug(data)     
        
        LOG.debug("status: {}".format(status)) 
        callback_msg='{\"Message\":\"The function descriptor ' + service_id + ' is in status: ' + status + '\"}'
        LOG.debug("callback_msg: {}".format(callback_msg)) 
        callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' " + " --data '" + str(callback_msg) + "'" + " " + callback_url
        LOG.debug("callback_post: {}".format(callback_post)) 
        call = subprocess.check_output([callback_post], shell=True)
        LOG.debug("call: {}".format(call)) 
        LOG.debug("callback end")  
        
              
    def getOSMVIMInfo(self,vim_id):
        LOG.info("get OSM get vim info starts")
        service_id = None 
        exists = 'NO'   
        token = self.__getOSMToken(request)
        LOG.debug(token)  
        url = self.authmanager.db_host.replace("http","https")      
        url_2 = url + ':9999/osm//admin/v1/vim_accounts/' + vim_id      
        vim_info = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "
        vim_info_2 = vim_info +token + "\"  " + url_2 
        LOG.debug(vim_info_2)       

        response = subprocess.check_output([vim_info_2], shell=True)
        LOG.debug(response)
        return response

    def getOSMVIMInfoURL(self,vim_info):
        LOG.info("get OSM get vim info url starts")
        
        content = json.loads(vim_info)
        LOG.debug(content)
        vim_url_full = content['vim_url']
        vim_url_array = vim_url_full.split(":")
        vim_url_center = vim_url_array[1]
        return vim_url_center[2:]    