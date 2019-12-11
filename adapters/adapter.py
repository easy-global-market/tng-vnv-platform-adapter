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
from adapters.authmanager import AuthManager
from adapters.osmmanager import OsmManager
from adapters.onapmanager import OnapManager

LOG = TangoLogger.getLogger("adapter", log_level=logging.DEBUG, log_json=True)

LOG.setLevel(logging.DEBUG)
#LOG.info("Hello world.")

FILE = "db-config.cfg"

class Adapter:

    def __init__(self, name):
        
        logging.getLogger().setLevel(logging.DEBUG)
        
        self.name = name
        self.host = "host"
        self.type = "type" 
        
        LOG.info("AdapterConstructor starts calls to db")
        self.authmanager = AuthManager(name)
        self.osmmanager = OsmManager(self.authmanager)
        self.onapmanager = OnapManager(self.authmanager)
         

    #######################OSM
    def getOSMServiceId(self,name,vendor,version):
        return self.osmmanager.getOSMServiceId(name,vendor,version)
    
    def deleteOSMService(self,id_to_delete):
        return self.osmmanager.deleteOSMService(id_to_delete)
    
    def deleteOSMFunction(self,id_to_delete):
        return self.osmmanager.deleteOSMFunction(id_to_delete) 
    
    def getOSMTokenForDelete(self):
        return self.osmmanager.getOSMTokenForDelete() 
    
    def getOSMInstaceStatus(self,service_id):
        return self.osmmanager.getOSMInstaceStatus(service_id) 
    
    def OSMInstantiateCallback(self,callback_url,inst_resp_yaml):
        return self.osmmanager.OSMInstantiateCallback(callback_url,inst_resp_yaml) 

    def OSMTerminateStatus(self,url_2,ns_id):
        return self.osmmanager.OSMTerminateStatus(url_2,ns_id) 
    
    def getUploadedOSMServiceId(self,upload_service):
        return self.osmmanager.getUploadedOSMServiceId(upload_service) 

    def createFunctionsArray(self,package_path):
        return self.osmmanager.createFunctionsArray(package_path)
     
    def uploadOSMService(self,request):  
        return self.osmmanager.uploadOSMService(request)
        
    def uploadOSMFunctionAndFiles(self,function_file_path,package_path):
        return self.osmmanager.uploadOSMFunctionAndFiles(function_file_path,package_path)


    def uploadOSMFunctionAndTarFiles(self,function_file_path,package_path):
        return self.osmmanager.uploadOSMFunctionAndTarFiles(function_file_path,package_path)

    def uploadOSMFunction(self,request):
        return self.osmmanager.uploadOSMFunction(request)
        
    def deleteOSMDescriptors(self,instance_id):
        return self.osmmanager.deleteOSMDescriptors(instance_id)
    
    def osmInstantiationIPs(self,request): 
        return self.osmmanager.osmInstantiationIPs(request)   
    
    def functionRecordOSM(self, vnfr_id):
        return self.osmmanager.functionRecordOSM(vnfr_id)

    def functionDescriptorOSM(self, vnfd_id):
        return self.osmmanager.functionDescriptorOSM(vnfd_id)
    
    def __getOSMToken(self,request):
        return self.osmmanager.getOSMToken(request)
    
    #######################ONAP
    #UNUSED
    
    
    def getVnVONAPServiceId(self,name,vendor,version):    
        return self.onapmanager.getVnVONAPServiceId(name,vendor,version)   
    
    def getSPONAPServiceId(self,name,vendor,version):        
        return self.onapmanager.getSPONAPServiceId(name,vendor,version) 

    def getONAPInstance(self,instance_id,service_name):        
        return self.onapmanager.getONAPInstance(instance_id,service_name)        

    def instantiateONAP(self,externalId, service_instance_name, auto_service_id):
        return self.onapmanager.instantiateONAP(externalId, service_instance_name, auto_service_id)       

    def terminateONAP(self,externalId, service_instance_name, auto_service_id):
        return self.onapmanager.terminateONAP(externalId, service_instance_name, auto_service_id)  
    
    
    def uploadPackage(self,package):
        LOG.info("upload package starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':               
            url = self.authmanager.db_host + ':32002/api/v3/packages'
            
            files = {'package': open(package,'rb')}
            upload = requests.post(url, files=files)
            LOG.debug("upload: {}".format(upload.text))
            return upload.text

        if self.authmanager.db_type == 'onap':               
            url = self.authmanager.db_host + '/sdc/v1/catalog/services/{uuid}/resourceInstances/{resourceInstanceNormalizedName}/artifacts'            
            files = {'package': open(package,'rb')}
            upload = requests.post(url, files=files)
            if request.method == 'POST':
                return upload.text

    
    
    def uploadPackageStatus(self,process_uuid):

        status = None
        LOG.info("uploadPackageStatusstarts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        url = self.authmanager.db_host + ':32002/api/v3/packages/status/' + process_uuid            
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
                      
        user_id = self.authmanagerdb_username

        url = self.authmanagerdb_host + '8443:/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products//versions//orchestration-template-candidate'                       
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

    def getPackages(self):    
        LOG.info("get packages starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        if self.authmanager.db_type == 'sonata':               
            url = self.authmanager.db_host + ':32002/api/v3/packages'
            
            response = requests.get(url, headers=JSON_CONTENT_HEADER)    
            if response.ok:        
                    LOG.debug("packages: {}".format(response.text.__str__()))
                    return response.text
        if self.authmanager.db_type == 'osm': 
            return "osm packages"



    def getPackage(self,name,vendor,version):    
        LOG.info("get package starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'} 

        if self.authmanager.db_type == 'sonata':    

            url = self.authmanager.db_host + ':32002/api/v3/packages'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            pkg = [x for x in jjson if x['pd']['name'] == name and x['pd']['vendor'] == vendor and x['pd']['version'] == version]
            
            if response.ok: 
                    LOG.debug(pkg)
                    return jsonify(pkg)

    def deletePackage(self,name,vendor,version):    
        LOG.info("delete package starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':    
            url = self.authmanager.db_host + ':32002/api/v3/packages'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            pkg = [x for x in jjson if x['pd']['name'] == name and x['pd']['vendor'] == vendor and x['pd']['version'] == version]
            
            if pkg:
                LOG.info(pkg)

                uuid_to_delete_1 = [obj['uuid'] for obj in jjson if(obj['pd']['name'] == name)]                            
                uuid_0 = uuid_to_delete_1.__str__()
                uuid_to_delete_2 = uuid_0[2:]
                uuid_to_delete_3 = uuid_to_delete_2[:-2]
                url_for_delete = url + '/' + uuid_to_delete_3
                LOG.debug(url_for_delete)
                delete = requests.delete(url_for_delete, headers=JSON_CONTENT_HEADER)

            if response.ok:                 
                    LOG.debug(delete.text)
                    return (delete.text, delete.status_code, delete.headers.items())
                    



    def getPackagebyId(self,name,vendor,version):    
        LOG.info("get package id starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'} 
        
        if self.authmanager.db_type == 'sonata':              
            url = self.authmanager.db_host + ':32002/api/v3/packages'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            pkg = [x for x in jjson if x['pd']['name'] == name and x['pd']['vendor'] == vendor and x['pd']['version'] == version]
            
            if pkg:
                LOG.debug("pkg: {}".format(pkg))
                uuid_to_delete_1 = [obj['uuid'] for obj in jjson if(obj['pd']['name'] == name)]                          
                uuid_0 = uuid_to_delete_1.__str__()
                uuid_to_delete_2 = uuid_0[2:]                
                uuid_to_delete_3 = uuid_to_delete_2[:-2]                
                url_for_delete = url + '/' + uuid_to_delete_3                
                delete = requests.get(url_for_delete, headers=JSON_CONTENT_HEADER)
            if response.ok:                 
                    LOG.debug(delete.text)
                    return (delete.text, delete.status_code, delete.headers.items())                


    def getOSMFunctionName(self,function_file_path):
        LOG.debug (function_file_path)
        function_name_array = function_file_path.split('/')
        LOG.debug (function_name_array)
        function_name = function_name_array[-1]
        #function_path_without_function = function_name_array[-2]
        LOG.debug (function_name) 
        return function_name   

    def getOSMFunctionPath(self,function_file_path):
        LOG.debug (function_file_path)
        function_name_array = function_file_path.split('/')
        LOG.debug (function_name_array)
        #function_name = function_name_array[-1]
        function_path_without_function = function_name_array[-2]
        LOG.debug (function_path_without_function) 
        return function_path_without_function          
    
    def getDownloadedPackageFolder(self,package_path):
        LOG.debug(package_path)
        package_path_array = package_path.split('/')
        LOG.debug(package_path_array)
        package_folder = package_path_array[-1]
        LOG.debug(package_folder)
        return package_folder
    


    def getOSMFunctionFiles(self,function_file_path,package_path):
        LOG.debug ("getOSMFunctionFiles starts")
        LOG.debug (function_file_path)
        LOG.debug (package_path)
        function_with_files = None
        function_with_files = []        
        function_name = self.getOSMFunctionName(function_file_path)
        napd_path = package_path + '/TOSCA-Metadata/NAPD.yaml'
        LOG.debug (napd_path)
        with open(napd_path) as n:
            napd = yaml.load(n)
        LOG.debug (napd)

        function_with_files.append(function_name)

        package_content = napd['package_content']

        for pc in package_content:
            LOG.debug(pc)
            if pc['source'] == function_name:
                LOG.debug("this is the function")
                function_tags = pc['tags']
                for ft in function_tags:
                    LOG.debug (ft)
                    try:
                        function_tags_array = ft.split('/')	
                        LOG.debug (function_tags_array[1])
                        if function_tags_array[0] == 'file-ref:cloud_init':	                        			
                            LOG.debug (function_tags_array[0])
                            function_file_path = '/cloud_init/' + function_tags_array[1]
                            LOG.debug (function_file_path)

                            #function_with_files.append(function_name)
                            function_with_files.append(function_file_path)
                    except:
                        LOG.debug ("split failed, trying next tag")

        LOG.debug (" ")
        LOG.debug (function_with_files)
        LOG.debug (" ")

        return function_with_files 

    def getOSMFunctionTarFile(self,function_file_path,package_path):
        LOG.debug ("getOSMFunctionTarFiles starts")
        LOG.debug (function_file_path)
        LOG.debug (package_path)
        function_with_files = None
        function_with_files = []        
        function_name = self.getOSMFunctionName(function_file_path)
        napd_path = package_path + '/TOSCA-Metadata/NAPD.yaml'
        LOG.debug (napd_path)
        with open(napd_path) as n:
            napd = yaml.load(n)
        LOG.debug (napd)
        LOG.debug ("ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        LOG.debug (" ")
        #function_with_files.append(function_name)

        package_content = napd['package_content']

        for pc in package_content:
            LOG.debug(pc)
            if pc['source'] == function_name:
                LOG.debug("this is the function")
                function_tags = pc['tags']
                LOG.debug (function_tags)
                for ft in function_tags:
                    LOG.debug (ft)
                    try:       
                        function_tags_array = ft.split('/')	            
                        if function_tags_array[0] == 'files':	                            	
                            LOG.debug (function_tags_array[0])                          			
                            LOG.debug (function_tags_array[1])
                            function_file_path =  function_tags_array[1]
                            LOG.debug (function_file_path)

                            #function_with_files.append(function_name)
                            function_with_files.append(function_file_path)                            
                    except:
                        function_with_files.append(function_name)
                        LOG.debug ("split failed, trying next tag")

        LOG.debug (" ")
        LOG.debug (function_with_files)
        LOG.debug (" ")

        return function_with_files[0]         




    def createTarOSMFunction(self,function_with_files,package_path):
        LOG.info("createTarOSMFunction starts")
        LOG.debug(function_with_files)
        LOG.debug(package_path)
        package_folder = self.getDownloadedPackageFolder(package_path)
        LOG.debug (package_folder)
        tarring = 'tar -czvf test.tar.gz '
        for fc in function_with_files:
            LOG.debug (fc)
            tarring = tarring + package_folder + '/' + fc + ' '      
        LOG.debug (tarring)     
        LOG.debug(function_with_files)
        create_tar = subprocess.check_output([tarring], cwd="/app/packages", shell=True)
        LOG.debug (create_tar)
        return (create_tar)
 

    

    def getServices(self):    
        LOG.info("get services starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
        #LOG.debug(self.authmanager.db_type)
        if self.authmanager.db_type == 'sonata':                        
            url = self.authmanager.db_host + ':32002/api/v3/services'
            LOG.debug(url)
            response = requests.get(url, headers=JSON_CONTENT_HEADER)    
            if response.ok:        
                    LOG.debug(response.text)
                    return (response.text, response.status_code, response.headers.items()) 

        if self.authmanager.db_type == 'osm':                
            token = self.__getOSMToken(request)
            LOG.debug(token)
            url = self.authmanager.db_host + ':9999/osm/nsd/v1/ns_descriptors'
            url_2 = url.replace("http","https")
            LOG.debug(url_2)
            
            services_nsd = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/zip\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            services_nsd_2 = services_nsd +token + "\" "  + url_2
            LOG.debug(services_nsd_2)
            services = subprocess.check_output([services_nsd_2], shell=True)
            LOG.debug(services)
            return (services) 

    def getFunctions(self):    
        LOG.info("get functions starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  

        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/functions'
            response = requests.get(url, headers=JSON_CONTENT_HEADER)    
            if response.ok:        
                    LOG.debug(response.text)
                    return (response.text, response.status_code, response.headers.items()) 

        if self.authmanager.db_type == 'osm':                
            token = self.__getOSMToken(request)
            LOG.debug(token)
            url = self.authmanager.db_host + ':9999/osm/vnfpkgm/v1/vnf_packages'
            url_2 = url.replace("http","https")
            LOG.debug(url_2)
            
            functions_vnfd = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/zip\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            functions_vnfd_2 = functions_vnfd +token + "\" "  + url_2
            LOG.debug(functions_vnfd_2)
            functions = subprocess.check_output([functions_vnfd_2], shell=True)
            LOG.debug(functions)
            return (functions)          

    def getService(self,name,vendor,version):    
        LOG.info("get service starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  

        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/services'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            pkg = [x for x in jjson if x['nsd']['name'] == name and x['nsd']['vendor'] == vendor and x['nsd']['version'] == version]            
            if response.ok: 
                    LOG.debug(pkg)
                    return jsonify(pkg)     

    def getServiceInstantiations(self,name,vendor,version):    
        LOG.info("get service instantiations starts")

        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  

        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/requests'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content

            LOG.debug(response_json)

            jjson = json.loads(response.content)
            LOG.debug(jjson)

            idd = LOG.debug(jjson[0]['service']['uuid'])
            idd = LOG.debug(jjson[0]['service']['name'])
            idd = LOG.debug(jjson[1]['service']['uuid'])
            idd = LOG.debug(jjson[1]['service']['name'])                       
            N = 0
            for N in range(10000):
                LOG.debug(jjson['service']['uuid'])
                N = N + 1
                LOG.debug(N)

            if response.ok:            
                return jsonify("no")
                            


    def getServiceId(self,name,vendor,version):    
        LOG.info("get service id in the SP starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/services'  
            #LOG.debug(name,vendor,version)
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            LOG.debug(response_json)
            jjson = json.loads(response_json)
            for x in jjson:
                LOG.debug(x)
                try:
                    if ( x['nsd']['name'] == name and x['nsd']['vendor'] == vendor and x['nsd']['version'] == version ) :
                        LOG.debug("this is the correct service")
                        uuid = x['uuid']
                        LOG.debug(uuid)
                        return uuid  
                except:
                    LOG.debug("this descriptor is not a Sonata one")
        
        LOG.debug(uuid)
        return uuid              


    def getPackageId(self,name,vendor,version):    
        LOG.info("get package id starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/packages'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            LOG.debug(response_json)
            jjson = json.loads(response_json)
            pkg = [x for x in jjson if x['pd']['name'] == name and x['pd']['vendor'] == vendor and x['pd']['version'] == version]
            
            if pkg:
                LOG.debug(pkg)
                uuid_to_delete_1 = [obj['uuid'] for obj in jjson if(obj['pd']['name'] == name)]                            
                uuid_0 = uuid_to_delete_1.__str__()
                uuid_to_delete_2 = uuid_0[2:]                
                uuid_to_delete_3 = uuid_to_delete_2[:-2]                
                url_for_delete = url + '/' + uuid_to_delete_3                
                delete = requests.get(url_for_delete, headers=JSON_CONTENT_HEADER)        
            if response.ok:                                        
                    LOG.debug(uuid_to_delete_3)
                    return uuid_to_delete_3

    def getPackageFile(self,pkg_id):    
        LOG.info("get package file starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
        if self.authmanager.db_type == 'sonata':                
            url = self.authmanager.db_host + ':32002/api/v3/packages'  
            url_2 = url + "/" + pkg_id + "/package-file --output temp-file.tgo"
            LOG.debug(url_2)          
            response = requests.get(url_2,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            LOG.debug(response_json)
            if response.ok:    
                LOG.debug(response.text)    
                return (response.text, response.status_code, response.headers.items())                  

    def instantiationStatus(self,request):    
        LOG.info("instantiation status starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        error = "error"

        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests/' +  request            
            time.sleep(2)
            LOG.debug(url)            
            try:
                response = requests.get(url,headers=JSON_CONTENT_HEADER)
                LOG.debug(response) 
                LOG.debug(response.text) 
                response_json = response.content
                LOG.debug(response_json)            
                if response.ok:        
                    LOG.debug(response.text)
                    return (response.text)
            except:
                return error

        if self.authmanager.db_type == 'osm':
            token = self.__getOSMToken(request)
            LOG.debug(token)
            ns_id = request
            LOG.debug(ns_id)                        
            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances'
            url_2 = url.replace("http","https")
            LOG.debug(url_2)            
            status_ns = "curl -s --insecure  -H \"Content-type: application/yaml\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "
            status_ns_2 = status_ns +token + "\" "
            status_ns_3 = status_ns_2 + " " + url_2 + "/" + ns_id          
            LOG.debug(status_ns_3)
            status = subprocess.check_output([status_ns_3], shell=True)
            status = subprocess.check_output([status_ns_3], shell=True)
            LOG.debug(status)
            return (status)       
         
    def instantiationsStatus(self):    
        LOG.info("instantatiations status starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests'  
            LOG.debug(url)            
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            LOG.debug(response_json)
            if response.ok: 
                LOG.debug(response.text)       
                return (response.text, response.status_code, response.headers.items())
            else:
                LOG.debug("response ko")
        if self.authmanager.db_type == 'osm':
            token = self.__getOSMToken(request)
            LOG.debug("OSM token : "+token)
            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances'
            url_2 = url.replace("http","https")
            LOG.debug(url_2)            
            instances_1 = "curl -s --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "                    
            instances_2 = instances_1 +token + "\" "  + url_2
            LOG.debug("instances"+ instances_2)        
            ns_instances = subprocess.check_output([instances_2], shell=True)
            return (ns_instances)         

    def instantiation(self,request):    
        LOG.info("instantiation starts")
        LOG.info("request: {}".format(request.__str__()))
        JSON_CONTENT_HEADER = {'content-Type':'application/json'}   

        if self.authmanager.db_type == 'onap':
            '''
            LOG.debug('this SP is ONAP')
            sp_host_2 = self.getHostIp()
            LOG.debug("sp2 es: ")
            LOG.debug(sp_host_2)
            url = sp_host_2 + '}/serviceInstances/v4'
            LOG.debug(url)
            LOG.debug(request_str.get_json())
            data = request_str.get_json()
            LOG.debug(url)
            LOG.debug(data)
            instantiate = requests.post( url, data=json.dumps(data), headers=JSON_CONTENT_HEADER)            
            LOG.debug(instantiate)
            if request.method == 'POST':
                return instantiate.text 
            '''           
        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests'
            LOG.debug(url)
            try:         
                instantiate = requests.post( url, data=request, headers=JSON_CONTENT_HEADER)                      
                LOG.debug("THIS IS THE INSTANTIATE RESPONSE:")
                LOG.debug(instantiate)
                LOG.debug(instantiate.text)
                return instantiate.text
            except:
                LOG.error("Error sending the request, check the connection and logs")
                msg = "{\"error\": \"error sending the request, check the connection and logs\"}"
                return msg                  

        if self.authmanager.db_type == 'osm':
            content = json.loads(request.__str__())
            LOG.info("osm-request: {}".format(content))
            token = self.__getOSMToken(request)
            #content = request.get_json()           
            
            vim_id = self.getVimId(self.authmanager.vim_account)
            LOG.info("vim_id : {}".format(vim_id))
            LOG.info("nsd_name : {}".format(content['nsd_name']))
            #nsd_id = self.getOSMNsdId(content['nsd_name'])
            nsd_id = content['nsd_name']
            ns_name = content['ns_name']
            
            LOG.info("nsd_id : {}".format(nsd_id))
            
            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances_content'
            url_2 = url.replace("http","https")
            LOG.debug("ns_instances_content endpoint : "+url_2)

            HEADERS = {
                'Accept':'application/json',
                'Content-Type':'application/json', 
                'Authorization':'Bearer ' +token+''                
            }     

            data_inst = {
                'nsdId':''+nsd_id+'',
                'nsName':''+ns_name+'',
                'vimAccountId':''+vim_id+''
            }       
            
            instantiate_nsd = "curl -s -X POST --insecure -H \"Content-type: application/yaml\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "                
            instantiate_nsd_2 = instantiate_nsd +token + "\" "
            instantiate_nsd_3 = instantiate_nsd_2 + " --data \"" + str(data_inst) + "\""
            instantiate_nsd_4 = instantiate_nsd_3 + " " + url_2
            LOG.info("instantiate_nsd : {}".format(instantiate_nsd_4) )

            inst = subprocess.check_output([instantiate_nsd_4], shell=True)

            try:
                callback_url = content['callback']
                LOG.debug("Callback url specified")
                _thread.start_new_thread(self.osmmanager.OSMUploadServiceCallback, (token,url_2,callback_url,inst))
            except:
                LOG.debug("No callback url specified")                

            LOG.debug(inst)
            return (inst)

    def instantiationDelete(self,request):    
        LOG.info("instantiation delete starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'onap':
            content = request.get_json()
            ns_instance_id = content['ns_instance_id']
            LOG.debug(ns_instance_id) 
            url = self.authmanager.db_host + '/ns/' + ns_instance_id
            LOG.debug(url)                    
            terminate = requests.delete(url,headers=JSON_CONTENT_HEADER) 
            if request.method == 'POST':
                LOG.debug(terminate.text)
                return terminate.text

        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests'
            LOG.debug(url)
            LOG.debug(request)            
            #LOG.debug(request)
            #LOG.debug(type(request))
            
            content = json.loads(request)
            instance_uuid = content['instance_uuid']    
            LOG.debug(instance_uuid)
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)

            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
            #terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"request_type\":\"TERMINATE_SERVICE\"}"
            
            LOG.debug(terminate_str)            
            delete_ns = "curl -s -X POST --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -d '" + terminate_str + "' " + url
            LOG.debug(delete_ns)

            terminate = subprocess.check_output([delete_ns], shell=True)
            LOG.debug(terminate)
            content = json.loads(request)
            ns_id = content['instance_uuid']
            LOG.debug(ns_id)


            #termination_request_json_dumps = json.dumps(terminate)
            #LOG.debug(termination_request_json_dumps)
            termination_request_json = json.loads(terminate)
            LOG.debug(termination_request_json)
            LOG.debug(termination_request_json['id'])
            termination_request_id = termination_request_json['id']        
            LOG.debug(termination_request_id)



            # deleting the descriptors
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)        
            if ( package_uploaded == True ) or ( package_uploaded == "true" ) or ( package_uploaded == "True" ):
                LOG.debug(ns_id)
                try:
                    LOG.debug(ns_id)
                    #request_status = self.SonataTerminateStatus(ns_id)
                    request_status = self.getRequestStatus(termination_request_id)
                    LOG.debug(request_status)
                    while request_status != 'READY':
                        time.sleep(5)
                        request_status = self.getRequestStatus(termination_request_id)
                        #request_status = self.SonataTerminateStatus(ns_id)      
                        LOG.debug(request_status)  
                    descriptor_reference_id = self.SonataTerminateDescriptorReference(ns_id)
                    LOG.debug(descriptor_reference_id)
                    name = self.SonataTerminateDescriptorName(descriptor_reference_id)
                    LOG.debug(name)
                    vendor = self.SonataTerminateDescriptorVendor(descriptor_reference_id)
                    LOG.debug(vendor)
                    version = self.SonataTerminateDescriptorVersion(descriptor_reference_id)
                    LOG.debug(version)
                    delete_descriptors = self.deletePackagefromService(name,vendor,version)                
                    LOG.debug(delete_descriptors) 
                except:
                    LOG.debug("error trying to delte the tgo from the SP")
                    
            LOG.debug(terminate)
            return terminate

        if self.authmanager.db_type == 'osm':
            LOG.debug(request)
            LOG.debug(url)
            token = self.__getOSMToken(request)
            LOG.debug(token)

            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances_content'
            url_2 = url.replace("http","https")
            
            content = json.loads(request)
            ns_id = content['instance_uuid']
            LOG.debug(ns_id)
            
            
            LOG.debug(ns_id)
            delete_ns = "curl -s -X DELETE --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "
            delete_ns_2 = delete_ns +token + "\" "
            delete_ns_3 = delete_ns_2 + " " + url_2 + "/" + ns_id          
            LOG.debug(delete_ns_3)

            # terminating the instance
            terminate = subprocess.check_output([delete_ns_3], shell=True)
            # deleting the descriptors
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)
            if ( package_uploaded == True ) or ( package_uploaded == "true" ) or ( package_uploaded == "True" ):
                instance_status = self.OSMTerminateStatus(url_2,ns_id)
                LOG.debug(instance_status)
                while instance_status != 'terminated':
                    time.sleep(2)
                    instance_status = self.OSMTerminateStatus(url_2,ns_id)
                delete_descriptors = self.deleteOSMDescriptors(ns_id)
                
                LOG.debug(delete_descriptors)

            LOG.debug(terminate)
            #_thread.start_new_thread(self.OSMUploadServiceCallback, (token,url_2,callback_url,content['ns_id']))
                                 
            LOG.debug(terminate)
            return (terminate)            


    def SonataTerminateStatus(self,ns_id):
        LOG.debug("SonataTerminateStatus begins")
        JSON_CONTENT_HEADER = {'Accept':'application/json'} 
        url = self.authmanager.db_host + ':32002/api/v3/records/services/' + ns_id
        LOG.debug(url)        
        service_record = requests.get(url,headers=JSON_CONTENT_HEADER) 
        LOG.debug("this is the network service record:")
        LOG.debug(service_record.text)
        service_record_json = json.loads(service_record.text)
        LOG.debug(service_record_json)
        instance_status = service_record_json['status']
        return instance_status

    def SonataTerminateDescriptorReference(self,ns_id):
        LOG.debug("SonataTerminateDescriptorReference begins")
        JSON_CONTENT_HEADER = {'Accept':'application/json'} 
        url = self.authmanager.db_host + ':32002/api/v3/records/services/' + ns_id
        LOG.debug(url)        
        service_record = requests.get(url,headers=JSON_CONTENT_HEADER) 
        LOG.debug(service_record.text)
        service_record_json = json.loads(service_record.text)
        LOG.debug(service_record_json)
        instance_descriptor_reference = service_record_json['descriptor_reference']
        return instance_descriptor_reference


    def SonataTerminateDescriptorName(self,descriptor_reference_id):
        LOG.debug("SonataTerminateDescriptorName begins")
        JSON_CONTENT_HEADER = {'Accept':'application/json'} 
        url = self.authmanager.db_host + ':32002/api/v3/services/' + descriptor_reference_id
        LOG.debug(url)        
        service_descriptor= requests.get(url,headers=JSON_CONTENT_HEADER) 
        LOG.debug(service_descriptor.text)
        service_descriptor_json = json.loads(service_descriptor.text)
        LOG.debug(service_descriptor_json)
        service_descriptor_name = service_descriptor_json['nsd']['name']
        return service_descriptor_name

    def SonataTerminateDescriptorVendor(self,descriptor_reference_id):
        LOG.debug("SonataTerminateDescriptorVendor begins")
        JSON_CONTENT_HEADER = {'Accept':'application/json'} 
        url = self.authmanager.db_host + ':32002/api/v3/services/' + descriptor_reference_id
        LOG.debug(url)        
        service_descriptor= requests.get(url,headers=JSON_CONTENT_HEADER) 
        LOG.debug(service_descriptor.text)
        service_descriptor_json = json.loads(service_descriptor.text)
        LOG.debug(service_descriptor_json)
        service_descriptor_vendor = service_descriptor_json['nsd']['vendor']
        return service_descriptor_vendor
    
    def SonataTerminateDescriptorVersion(self,descriptor_reference_id):
        LOG.debug("SonataTerminateDescriptorVersion begins")
        JSON_CONTENT_HEADER = {'Accept':'application/json'} 
        url = self.authmanager.db_host + ':32002/api/v3/services/' + descriptor_reference_id
        LOG.debug(url)        
        service_descriptor= requests.get(url,headers=JSON_CONTENT_HEADER) 
        LOG.debug(service_descriptor.text)
        service_descriptor_json = json.loads(service_descriptor.text)
        LOG.debug(service_descriptor_json)
        service_descriptor_version = service_descriptor_json['nsd']['version']
        return service_descriptor_version


         
        
    



    def getWims(self):    
        LOG.info("get wims starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        if self.authmanager.db_type == 'sonata':
            curl_vims = 'curl -s ' + self.authmanager.db_host + ':32002/api/v3/settings/wims'
            LOG.debug("curl_vims_call: {}".format(curl_vims))
            vims = subprocess.check_output([curl_vims], shell=True)
            LOG.debug("vims: {}".format(vims))
            return vims

    def getVims(self):    
        LOG.info("get vims starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            curl_vims = 'curl -s ' + self.authmanager.db_host + ':32002/api/v3/settings/vims'
            LOG.debug("curl_vims_call: {}".format(curl_vims))
            vims = subprocess.check_output([curl_vims], shell=True)
            LOG.debug("vims: {}".format(vims))
            return vims

        if self.authmanager.db_type == 'osm':
            token = self.__getOSMToken(request)
            url = self.authmanager.db_host + ':9999/osm/admin/v1/vim_accounts'
            url_2 = url.replace("http","https")
            
            vimss = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/zip\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            vimss_2 = vimss +token + "\" "  + url_2
            LOG.debug("curl_vims_call: {}".format(vimss_2))
            vims = subprocess.check_output([vimss_2], shell=True)
            #return jsonify(upload_nsd_4) 
            LOG.debug("vims: {}".format(vims))
            return (vims)              

    def getWim(self,vim):    
        LOG.info("get wim starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        if self.authmanager.db_type == 'sonata':
            curl_vim = 'curl -s ' + self.authmanager.db_host + ':32002/api/v3/settings/wims/' + vim
            LOG.debug("curl_vim: {}".format(curl_vim))
            vim = subprocess.check_output([curl_vim], shell=True)
            LOG.debug("wim: {}".format(vim))
            return vim

    def getVim(self,vim):    
        LOG.info("get vim starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            curl_vim = 'curl -s ' + self.authmanager.db_host + ':32002/api/v3/settings/vims/' + vim
            LOG.debug("curl_vim: {}".format(curl_vim))
            vim = subprocess.check_output([curl_vim], shell=True)
            LOG.debug("vim: {}".format(vim))
            return vim

        if self.authmanager.db_type == 'osm':
            token = self.__getOSMToken(request)
            url = self.authmanager.db_host + ':9999/osm/admin/v1/vim_accounts'
            url_2 = url.replace("http","https")
            
            vimss = "curl -s --insecure -w \"%{http_code}\" -H \"Content-type: application/zip\"  -H \"Accept: application/yaml\" -H \"Authorization: Bearer "
            vimss_2 = vimss +token + "\" "  + url_2 + "/" + vim
            LOG.debug("vim_curl: {}".format(vimss_2))
            vims = subprocess.check_output([vimss_2], shell=True)
            LOG.debug("vims: {}".format(vims))
            return (vims) 
   


    def getVimId(self,vim):    
        LOG.info("get vim id starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        
        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests'  
            return url

        if self.authmanager.db_type == 'osm':
            url = self.authmanager.db_host.replace("http://","")
            url = url.replace("https://","")
            get_vim = "osm --user "+self.authmanager.db_username+" --password '"+self.authmanager.db_password+"' --hostname " + url + " vim-show " + vim
            LOG.debug("get_vim: {}".format(get_vim))
            
            try:
                vim_info = subprocess.check_output([get_vim], shell=True)
                s = json.dumps(str(vim_info))
                LOG.debug("OsmCliResponse: {}".format(s))
                start = s.find('_id')
                end = s.find('\\\" ', start)
                vim_id = s[start+20:end]
                LOG.debug("vim_id: "+vim_id+" - start : "+s[start+20:end])
                return vim_id
        
            except E:
                LOG.debug("Exception during osmclient call")
                raise
            
            return None




    def getOSMNsdId(self,nsd_name):    
        LOG.info("get osm nsd id starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'osm':
            get_nsd = "osm --hostname " + self.authmanager.db_host + "  nsd-show " + nsd_name
            LOG.debug("get_nsd: {}".format(get_nsd))
            nsd_info = subprocess.check_output([get_nsd], shell=True)
                    
            s = json.dumps(str(nsd_info))
            LOG.debug("nsd_info: {}".format(s)) 
            start = s.find('_id')
            end = s.find('\\\" ', start)
            LOG.debug(s[start+21:end])
            vim_id = s[start+21:end]    
            LOG.debug("vim_id: {}".format(vim_id))      
            return vim_id            

    def downloadPackageSonata(self,package_id):
        LOG.info("download package sonata starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}                              
        url = self.authmanager.db_host + ':32002/api/v3/packages'        
        url2 = 'curl -s ' + url + '/' + package_id + '/package-file --output /app/packages/' + package_id + '.tgo'        
        LOG.debug("curl_download_package: {}".format(url2))
        download = subprocess.check_output([url2], shell=True)
        msg = "Package downloaded to: " + "/app/packages/" + package_id + '.tgo' 
        LOG.debug("resp_download_pkg: {}".format(msg))
        return (msg)

     

    def monitoringTests(self,monitoring_type):
        LOG.info("monitoring tests starts")
        JSON_CONTENT_HEADER = {'Accept':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            LOG.debug('this SP is a Sonata')

        if self.authmanager.db_type == 'osm':
            current_string="date -u +\"%Y-%m-%dT%H:%M:%S.%3N\""          
            current_date = subprocess.check_output([current_string], shell=True)
            current_date_1 = current_date.__str__()
            current_date_2 = current_date_1.__str__()[2:25]
            yesterday_string="date -d \"1 days ago\" -u +\"%Y-%m-%dT%H:%M:%S.%3N\""
            yesterday_date = subprocess.check_output([yesterday_string], shell=True)
            yesterday_date_1 = yesterday_date.__str__()
            yesterday_date_2 = yesterday_date_1.__str__()[2:25]
            url = self.authmanager.db_host + ':9091/api/v1/query_range?query=osm_'
            url_2 = url.replace("http","https")
            LOG.debug(url_2) 
            monitoring_string = "curl \"" + url + monitoring_type + "&start="  + yesterday_date_2 + "Z&end=" + current_date_2 + "Z&step=15s\""
            LOG.debug(monitoring_string)
            monitoring_curl = subprocess.check_output([monitoring_string], shell=True)
            LOG.debug(monitoring_curl)
            return monitoring_curl

    def getSonataToken(self,request):            
        LOG.info("get sonata token starts")
        JSON_CONTENT_HEADER = {'Content-type':'application/json'}   
        url = self.authmanager.db_host + ':4567/login'
        url_2 = url.replace("http","https")
        LOG.debug(url_2)
        data_for_token= "{\"username\": \"" +self.authmanager.db_username+ "\", \"password\": \"" +self.authmanager.db_password+ "\"}"
        LOG.debug(data_for_token)   
        get_token = "curl -i -X POST -H Content-type: application/json -d '" + data_for_token + "' " + url 
        LOG.debug(get_token)
        token_curl = subprocess.check_output([get_token], shell=True)
        LOG.debug(token_curl)
        string = token_curl.__str__()
        start = string.find('{')
        end = string.find('}', start)
        tok = string[start:end+1]
        LOG.debug(tok)
        token_id_json = json.loads(tok)
        LOG.debug(token_id_json['token'])
        return token_id_json['token']  


    def getONAPToken(self,request):            
        LOG.info("get onap token starts")
        JSON_CONTENT_HEADER = {'Content-type':'application/json'}   
        url = self.authmanager.db_host + ':4567/login'
        url_2 = url.replace("http","https")
        LOG.debug(url_2)
        password_for_token = self.authmanager.db_password        
        data_for_token= "{\"username\": \"" +self.authmanager.db_username+ "\", \"password\": \"" +self.authmanager.db_password+ "\"}"
        LOG.debug(data_for_token)   
        get_token = "curl -i -X POST -H Content-type: application/json -d '" + data_for_token + "' " + url 
        LOG.debug(get_token)
        token_curl = subprocess.check_output([get_token], shell=True)
        LOG.debug(token_curl)
        string = token_curl.__str__()
        start = string.find('{')
        end = string.find('}', start)
        tok = string[start:end+1]
        LOG.debug(tok)
        token_id_json = json.loads(tok)
        LOG.debug(token_id_json['token'])
        return token_id_json['token']                    




    def downloadPackageTGO(self,package_id):
        LOG.info("dwnload package tgo starts")
        msg = None
        try:
            get_package_curl = 'curl -H \'Content-type: application/json\' http://tng-cat:4011/api/catalogues/v2/packages/' + package_id            
            package_json = subprocess.check_output([get_package_curl], shell=True)
            time.sleep(2)
            package_json_loaded = json.loads(package_json)

            package_file_uuid = package_json_loaded['pd']['package_file_uuid']       
            LOG.debug(package_file_uuid)

            get_tgo_curl = 'curl -H \'Content-type: application/zip\' http://tng-cat:4011/api/catalogues/v2/tgo-packages/' + package_file_uuid + ' --output /app/packages/' + package_file_uuid + '.tgo'                        
            LOG.debug(get_tgo_curl)    
            package_tgo = subprocess.check_output([get_tgo_curl], shell=True)
            time.sleep(2)
            msg = "{\"package\": \"/app/packages/" + package_file_uuid + ".tgo\"}" 
            LOG.debug(msg)
        except:
            msg = "error"
        return (msg)






    def getVnVPackages(self):    
        LOG.info("get vnv packages starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}
        url = 'http://tng-cat:4011/api/catalogues/v2/packages'
        response = requests.get(url, headers=JSON_CONTENT_HEADER)    
        if response.ok:        
            LOG.debug(response.text)
            return (response.text)

    def getSonataSPPackages(self):    
        LOG.info("get sonata sp packages starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}
        url = self.authmanager.db_host + ':32002/api/v3/packages'
        response = requests.get(url, headers=JSON_CONTENT_HEADER)    
        if response.ok:        
            LOG.debug(response.text)
            return (response.text)


    def getVnVPackagebyId(self,name,vendor,version):    
        LOG.info("get vnv packagae id starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'} 
        
        url = 'http://tng-cat:4011/api/catalogues/v2/packages'  

        try:
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            for x in jjson:
                if ( x['pd']['name'] == name and x['pd']['vendor'] == vendor and x['pd']['version'] == version ) :
                    uuid = x['uuid']
            LOG.debug(uuid)
            return uuid                   
        except:
            msg = "{\"error\": \"error getting the package id from the VnV catalogue\"}"
            return msg  
    

    def instantiationInfoMonitoringTest(self,id):    
        LOG.info("instantiation info monitoring starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            instance_request = self.instantiationStatus(id) 
            LOG.info(instance_request)               
            instance_request_json = json.loads(instance_request)
            instance_uuid = instance_request_json['instance_uuid']
            LOG.info(instance_uuid)

            response = "{\"ns_instance_uuid\": \"" + instance_uuid + "\",\"functions\":["

            url_records_services = self.authmanager.db_host + ':32002/api/v3/records/services/' + instance_uuid
            service_record = requests.get(url_records_services,headers=JSON_CONTENT_HEADER)
            LOG.info(service_record.text)
            service_record_json = json.loads(service_record.text)
            vnfr_array = service_record_json['network_functions']
            LOG.info(vnfr_array)
            for vnf in vnfr_array:
                function_record_uuid = vnf['vnfr_id']
                LOG.info(function_record_uuid)




                #response = response + "{\"vnfr_id\": \"" + function_record_uuid + "\","




                url_records_functions = url + ':32002/api/v3/records/functions/' + function_record_uuid
                function_record = requests.get(url_records_functions,headers=JSON_CONTENT_HEADER)
                function_record_json = json.loads(function_record.text)
                LOG.info(function_record_json)
                try:
                    function_vdu_array = function_record_json['cloudnative_deployment_units']
                    LOG.info(function_vdu_array)
                    for vdu in function_vdu_array:
                        #LOG.debug(vdu['vim_id'])
                        function_vim = vdu['vim_id']
                        cdu_reference = vdu['cdu_reference']
                        #LOG.debug(function_vim)
                        LOG.info(cdu_reference)
                        cdu_reference_splitted = cdu_reference.split(":")
                        #cnf_name = cdu_reference[0: cdu_reference.find(":") ]
                        cnf_name = cdu_reference_splitted[1]
                        container_name = cnf_name
                        LOG.info(cnf_name)

                        response = response + "{\"vnfr_id\": \"" + function_record_uuid + "\","

                        response = response + "\"container_name\": \"" + cnf_name + "\","
                        response = response + "\"pod_name\": \"" + cdu_reference + "\","
                        #response = response + "\"pod_name\": \"" + cnf_name + "\","
                        #response = response + "\"pod_name\": \"" + cdu_reference + "\","
                        response = response + "\"vim_id\": \"" + function_vim + "\","
                        vim_object= self.getVim(function_vim)
                        vim_json = json.loads(vim_object)
                        vim_endpoint = vim_json['endpoint']
                        response = response + "\"vim_endpoint\": \"" + vim_endpoint + "\"},"                 
                except:                    
                    function_vdu_array = function_record_json['virtual_deployment_units']
                    LOG.info(function_vdu_array)
                    for x in function_vdu_array:
                        LOG.info(x)
                        vi = x['vnfc_instance']
                        LOG.info(vi)
                        for y in vi:  
                            LOG.info(y)                                                                       
                            function_vim = y['vim_id']
                            function_vc = y['vc_id']
                            LOG.info(function_vim)
                            LOG.info(function_vc)
                            response = response + "\"vc_id\": \"" + function_vc + "\","
                            response = response + "\"vim_id\": \"" + function_vim + "\","
                            vim_object= self.getVim(function_vim)
                            vim_json = json.loads(vim_object)
                            vim_endpoint = vim_json['endpoint']
                            response = response + "\"vim_endpoint\": \"" + vim_endpoint + "\"},"

                response_2 = response[:-1]                
                response_2 = response_2 + "]"
                response_2 = response_2 + ",\"test_id\": \"null\""

            response_2 = response_2 + "}"
            return response_2




    def instantiationInfoMonitoring(self,id):    
        LOG.info("instantiation info monitoring starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            instance_request = self.instantiationStatus(id) 
            LOG.debug(instance_request)               
            instance_request_json = json.loads(instance_request)
            instance_uuid = instance_request_json['instance_uuid']
            LOG.debug(instance_uuid)

            response = "{\"ns_instance_uuid\": \"" + instance_uuid + "\",\"functions\":["

            url_records_services = self.authmanager.db_host + ':32002/api/v3/records/services/' + instance_uuid
            service_record = requests.get(url_records_services,headers=JSON_CONTENT_HEADER)
            LOG.debug(service_record.text)
            service_record_json = json.loads(service_record.text)
            vnfr_array = service_record_json['network_functions']
            LOG.debug(vnfr_array)
            for vnf in vnfr_array:
                function_record_uuid = vnf['vnfr_id']
                LOG.debug(function_record_uuid)

                #response = response + "{\"vnfr_id\": \"" + function_record_uuid + "\","

                url_records_functions = self.authmanager.db_host + ':32002/api/v3/records/functions/' + function_record_uuid
                function_record = requests.get(url_records_functions,headers=JSON_CONTENT_HEADER)
                function_record_json = json.loads(function_record.text)
                LOG.debug(function_record_json)
                try:
                    function_vdu_array = function_record_json['cloudnative_deployment_units']
                    LOG.debug(function_vdu_array)
                    for vdu in function_vdu_array:
                        #LOG.debug(vdu['vim_id'])
                        function_vim = vdu['vim_id']
                        cdu_reference = vdu['cdu_reference']
                        #LOG.debug(function_vim)
                        LOG.debug(cdu_reference)
                        cdu_reference_splitted = cdu_reference.split(":")
                        #cnf_name = cdu_reference[0: cdu_reference.find(":") ]
                        cnf_name = cdu_reference_splitted[1]
                        container_name = cnf_name
                        LOG.debug(cnf_name)

                        response = response + "{\"vnfr_id\": \"" + function_record_uuid + "\","

                        response = response + "\"container_name\": \"" + cnf_name + "\","
                        response = response + "\"pod_name\": \"" + cdu_reference + "\","
                        #response = response + "\"pod_name\": \"" + cnf_name + "\","
                        #response = response + "\"pod_name\": \"" + cdu_reference + "\","
                        response = response + "\"vim_id\": \"" + function_vim + "\","
                        vim_object= self.getVim(function_vim)
                        vim_json = json.loads(vim_object)
                        vim_endpoint = vim_json['endpoint']
                        response = response + "\"vim_endpoint\": \"" + vim_endpoint + "\"},"                 
                except:                    
                    function_vdu_array = function_record_json['virtual_deployment_units']
                    LOG.debug(function_vdu_array)
                    for x in function_vdu_array:
                        LOG.debug(x)
                        vi = x['vnfc_instance']
                        LOG.debug(vi)
                        for y in vi:  
                            LOG.debug(y)                                                                       
                            function_vim = y['vim_id']
                            function_vc = y['vc_id']
                            LOG.debug(function_vim)
                            LOG.debug(function_vc)
                            response = response + "\"vc_id\": \"" + function_vc + "\","
                            response = response + "\"vim_id\": \"" + function_vim + "\","
                            vim_object= self.getVim(function_vim)
                            vim_json = json.loads(vim_object)
                            vim_endpoint = vim_json['endpoint']
                            response = response + "\"vim_endpoint\": \"" + vim_endpoint + "\"},"

                response_2 = response[:-1]                
                response_2 = response_2 + "]"
                response_2 = response_2 + ",\"test_id\": \"null\""

            response_2 = response_2 + "}"
            return response_2

        if self.authmanager.db_type == 'osm':
            instance_request = self.instantiationStatus(id) 
            LOG.debug(instance_request) 
            instance_request_json =  json.loads(instance_request)
            ns_id = instance_request_json['ns-instance-config-ref']
            LOG.debug(ns_id)

            response = "{\"ns_instance_uuid\": \"" + ns_id + "\","
            response = response + "\"platform_type\": \"osm\","
            response = response + "\"functions\": ["

            vnfr_array = instance_request_json['constituent-vnfr-ref']
            LOG.debug(vnfr_array)
            response_functions = " "
            for vnfr_id in vnfr_array:
                LOG.debug("FUCNTIONS")
                LOG.debug(vnfr_id)
                response_function = "{\"vnfr_id\": \"" + vnfr_id + "\", \"function_type\": " + "\"vnf\","                

                function_request = self.functionRecordOSM(vnfr_id)
                function_request_json =  json.loads(function_request)
                LOG.debug(function_request_json)
                vnfd_name = function_request_json['vnfd-ref']  

                vim_id = function_request_json['vim-account-id'] 

                response_function = response_function + "\"name\": \"" + vnfd_name + "\","
                response_function = response_function + "\"endpoints\": ["
                vdur = function_request_json['vdur']                                
                LOG.debug(vdur)
                
                for vdu in vdur:
                    vc_id = vdu['vim-id']                                       
                    interfaces = vdu['interfaces']
                    LOG.debug(interfaces)
                    for interface in interfaces:                       
                        LOG.debug(interface)
                        address = interface['ip-address']
                        LOG.debug(address)
                        name = interface['name']
                        type = interface['name']
                        LOG.debug(name)
                        response_interface = "{\"name\": \"" + name + "\", \"type\": \"" + type + "\",\"address\":\"" + address + "\"" + "},"

                        response_function = response_function + response_interface

                response_function_2 = response_function[:-1]

                response_function = response_function_2 + "],"

                response_function = response_function + "\"vc_id\": \"" + vc_id + "\","
                response_function = response_function + "\"vim_id\": \"" + vim_id + "\","
                vim_info = self.osmmanager.getOSMVIMInfo(vim_id)
                vim_url = self.osmmanager.getOSMVIMInfoURL(vim_info)
                response_function = response_function + "\"vim_endpoint\": \"" + vim_url + "\","

                response_function_2 = response_function[:-1]
                response_function_2 = response_function_2 + "},"

                LOG.debug(response_function_2)
                response_functions = response_functions + response_function_2

            response_functions_2 = response_functions[:-1] 
            response_functions = response_functions_2 + "],"                        
            response = response + response_functions
            response = response + "\"test_id\": \"null\""
            response = response + "}"
            LOG.debug(response)
            return response            


    def unzipPackage(self,package):
        LOG.info("unzip package starts")
        import zipfile
        package_string = package.__str__()
        package_string_2 = package_string[:-4]
        LOG.debug(package_string_2)

        with zipfile.ZipFile(package,"r") as zip_ref:        
            zip_ref.extractall(package_string_2)
        
        msg_response = "The package " + package + " was unzipped to: " + package_string_2
        LOG.debug(msg_response)
        #return msg_response
        return package_string_2

    def instantiationInfoCurator(self,id):    
        LOG.info("instantiation info curator starts")
        k8s = None
        response_k8s = None
        response_k8s_2 = None
        response_3 = None
        function_record_uuid = None
        ports = None
        fip = None
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        sp_ip = self.getSPIp()   
        LOG.info ("sp ip: "+ sp_ip)

  

        if self.authmanager.db_type == 'sonata':
            instance_request = self.instantiationStatus(id) 
            LOG.debug(instance_request)               
            
            try:
                instance_request_json = json.loads(instance_request)
                instance_uuid = instance_request_json['instance_uuid']
                LOG.debug(instance_uuid)
            except:
                error = "error in the request"
                LOG.debug(error)
                msg = "{\"error\": \"error in the request, check the SP\"}"
                return msg

            response = "{\"ns_instance_uuid\": \"" + instance_uuid + "\","                
            response = response + "\"platform_type\": \"" + self.authmanager.db_type + "\","

            #response = response + "\"platform_ip\": \"" + sp_ip.__str__() + "\","
            response = response + "\"platform_ip\": \"" + sp_ip + "\","

            response = response + "\"functions\":["    

            url_records_services = self.authmanager.db_host + ':32002/api/v3/records/services/' + instance_uuid
            service_record = requests.get(url_records_services,headers=JSON_CONTENT_HEADER)
            LOG.debug(service_record.text)
            service_record_json = json.loads(service_record.text)
            vnfr_array = service_record_json['network_functions']
            LOG.debug(vnfr_array)
            for vnf in vnfr_array:
                function_record_uuid = vnf['vnfr_id']                
                LOG.debug(function_record_uuid)
                response = response + ",{"
                url_records_functions = self.authmanager.db_host + ':32002/api/v3/records/functions/' + function_record_uuid
                function_record = requests.get(url_records_functions,headers=JSON_CONTENT_HEADER)
                function_record_json = json.loads(function_record.text)
                LOG.debug(function_record_json)
                try:
                    function_vdu_array = function_record_json['cloudnative_deployment_units']
                    function_type = "cnf" 
                    cnf_name = None
                    response = response + "\"id\": \"" + function_record_uuid + "\","
                    response = response + "\"function_type\": \"" + function_type + "\","                    
                    k8s = "k8s"
                    
                    LOG.debug(function_vdu_array)
                    floating_ip = None
                    
                    for vdu in function_vdu_array:
                        LOG.debug(vdu)
                        cdu_reference = vdu['cdu_reference']
                        cnf_name = cdu_reference[0: cdu_reference.find(":") ]
                        LOG.debug(cnf_name)
                        LOG.debug(response)
                        connection_points = vdu['connection_points']
                        LOG.debug(connection_points)
                        ports = "\"ports\": ["
                        for c in connection_points:
                            port_id = c['id']
                            port_port = c['port']
                            port_type = c['type']
                            ports = ports + "{\"id\": \"" + port_id + "\",\"port\": \""
                            LOG.debug(response)
                            ports = ports + port_port.__str__() + "\"},"

                        response_ports = ports[:-1]
                        ports = response_ports + "]"
                       
                        LOG.debug(response)

                        try:
                            load_balancer_ip = vdu['load_balancer_ip']
                            LOG.debug(load_balancer_ip)                              
                            load_balancer_ip_str =  load_balancer_ip.__str__()
                            load_balancer_ip_str_replaced = load_balancer_ip_str.replace("'","\"")
                            lb_json = json.loads(load_balancer_ip_str_replaced)
                            fip_fip = lb_json['floating_ip']
                            LOG.debug(fip_fip)
                            LOG.debug(lb_json)
                            load_balancer_ip_str_replaced = load_balancer_ip_str.replace("'","\"")
                            LOG.debug(load_balancer_ip_str_replaced)
                            lb_1 = load_balancer_ip_str_replaced.split(",")
                            lb_2 = lb_1[1]
                            fip = "\"address\": \"" + fip_fip + "\""
                            LOG.debug(fip)
                        except:
                            LOG.debug("no load balancer")

                        LOG.debug(response)
                         
                    response = response + "\"name\": \"" + cnf_name + "\","
                    response = response + "\"endpoints\": [{"
                    response = response + "\"id\": \"" + "floating_ip" + "\"," 
                    response = response + "\"type\": \"" + "floating_ip" + "\","    
                    fip_ip = fip.replace("floating_ip","address")                    
                    fip_ip_2 = fip_ip.replace("internal_ip","address")
                    response = response + fip_ip_2 + ","
                    response = response + ports + "}]}"
                    response_2 = response[:-1]
                    response = response_2
                    response = response + "},"
                    response_k8s = response                                  
                except:
                    function_type = "vnf"                                        
                    function_vdu_array = function_record_json['virtual_deployment_units']
                    LOG.debug(function_vdu_array)
                    
                    for x in function_vdu_array:
                        LOG.debug(x)
                        vdu_reference = x['vdu_reference']
                        vdu_reference_2 = vdu_reference[0: vdu_reference.find(":") ]                                              
                        response = response + "\"function_type\": \"" + function_type + "\","
                        response = response + "\"name\": \"" + vdu_reference_2 + "\","
                        vi = x['vnfc_instance']
                        LOG.debug(vi)
                        for y in vi:  
                            LOG.debug(y)                                                                       
                            function_vim = y['vim_id']
                            function_vc = y['vc_id']
                            LOG.debug(function_vim)
                            LOG.debug(function_vc)

                            connection_points = y['connection_points']
                            LOG.debug(connection_points)
                            response = response + "\"endpoints\": ["

                            for z in connection_points:
                                LOG.debug(z)
                                port_id = z['id']
                                port_type = z['type']
                                port_interface = z['interface']
                                port_ip = port_interface['address']
                                response = response + "{\"id\": \"" + port_id + "\","
                                response = response + "\"type\": \"" + port_type + "\","
                                response = response + "\"address\": \"" + port_ip + "\"},"                                    
                            response_port = response[:-1]
                            response = response_port + "]"
                response_2 = response[:-1]                
                response_2 = response_2 + "]}]}"

            if k8s == "k8s":
                LOG.debug(k8s)
                response_k8s_2 = response_k8s[:-1]
                response_2 = response_k8s[:-1]
                response = response_2 + "]}"
                response_str_replaced = response.replace("[,","[") 
                response_str_replaced_2 = response_str_replaced.replace("},,","},") 
                LOG.debug(response_str_replaced_2)
                return response_str_replaced_2

            response_str_replaced = response_2.replace("[,","[") 
            response_str_replaced_2 = response_str_replaced.replace("],","]},") 
            LOG.debug(response_str_replaced_2)
            return response_str_replaced_2
        
        if self.authmanager.db_type == 'osm':
            instance_request = self.instantiationStatus(id) 
            LOG.debug(instance_request) 
            instance_request_json =  json.loads(instance_request)
            ns_id = instance_request_json['ns-instance-config-ref']
            LOG.debug(ns_id)

            response = "{\"ns_instance_uuid\": \"" + ns_id + "\","
            response = response + "\"platform_type\": \"osm\","

            response = response + "\"platform_ip\": \"" + sp_ip + "\","

            response = response + "\"functions\": ["

            vnfr_array = instance_request_json['constituent-vnfr-ref']
            LOG.debug(vnfr_array)
            response_functions = " "
            for vnfr_id in vnfr_array:
                LOG.debug("FUCNTIONS")
                LOG.debug(vnfr_id)
                response_function = "{\"id\": \"" + vnfr_id + "\", \"function_type\": " + "\"vnf\","                

                function_request = self.functionRecordOSM(vnfr_id)
                function_request_json =  json.loads(function_request)
                LOG.debug(function_request_json)
                
                #vnfd_name = function_request_json['vnfd-ref']  

                vnfd_id = function_request_json['vnfd-id'] 
                vnfd_request = self.functionDescriptorOSM(vnfd_id)
                vnfd_request_json = json.loads(vnfd_request)
                vnfd_name = vnfd_request_json['name']  

                response_function = response_function + "\"name\": \"" + vnfd_name + "\","
                response_function = response_function + "\"endpoints\": ["
                vdur = function_request_json['vdur']                                
                LOG.debug(vdur)
                for vdu in vdur:
                    interfaces = vdu['interfaces']
                    LOG.debug(interfaces)
                    for interface in interfaces:                       
                        LOG.debug(interface)
                        address = interface['ip-address']
                        LOG.debug(address)
                        
                        #name = interface['name']
                        name = interface['ns-vld-id']

                        type = interface['name']
                        LOG.debug(name)
                        response_interface = "{\"name\": \"" + name + "\", \"type\": \"" + type + "\",\"address\":\"" + address + "\"" + "},"

                        response_function = response_function + response_interface

                response_function_2 = response_function[:-1]
                response_function_2 = response_function_2 + "]},"

                LOG.debug("function-----function")
                LOG.debug(response_function_2)
                response_functions = response_functions + response_function_2

            response_functions_2 = response_functions[:-1] 

            response_functions = response_functions_2 + "]"
            
            response = response + response_functions
            response = response + "}"
            LOG.debug(response)
            return response

    


    def wait_for_instantiation(self,id):
        LOG.info("wait for instantiation starts")
        time.sleep(2)
        status = None
        while status == None:
            status =  self.getRequestStatus(id)
            LOG.debug(status)
            if status == None:
                time.sleep(7)
        while status == 'NEW':
            status =  self.getRequestStatus(id)
            LOG.debug(status)
            if status == 'NEW':
                time.sleep(7)        
        while status == 'INSTANTIATING':
            status =  self.getRequestStatus(id)
            LOG.debug(status)
            if status == 'INSTANTIATING':
                time.sleep(7)  
        if status == 'ERROR':
            status =  self.getRequestError(id)
            return "ERROR" 
        if status == 'READY':
            return status           
        LOG.debug(status)
        return status
        
    def getRequestError(self,id):
        LOG.info("get request error starts")
        time.sleep(5)        
        status_call = self.instantiationStatus(id)
        LOG.debug(status_call)
        instantiation_request_json_dumps = json.dumps(status_call)
        LOG.debug(instantiation_request_json_dumps)
        instantiation_request_json = json.loads(status_call)
        try:
            status = instantiation_request_json['error']
            LOG.debug(status)
            return (status)
        except:
            msg = "{\"error\": \"the record's status has no value\"}"
            return (msg) 


    def getRequestStatus(self,id):
        LOG.info("get request status starts")   
        status_call = None
        try:
            status_call = self.instantiationStatus(id)
        except:
            if status_call == "error":
                msg = "{\"error\": \"the curl for getting the request has failed\"}"
                return (msg)

        LOG.debug(status_call)
        instantiation_request_json_dumps = json.dumps(status_call)
        LOG.debug(instantiation_request_json_dumps)
        instantiation_request_json = json.loads(status_call)
        try:
            status = instantiation_request_json['status']
            LOG.debug(status)
            return (status)
        except:
            msg = "{\"error\": \"the record's status has no value\"}"
            return (msg) 

    def getRequestInstanceId(self,id):
        LOG.info("get request id starts")
        request = self.instantiationStatus(id)
        request_json = request.get_json()
        LOG.debug(request_json['instance_uuid'])
        return (request_json['instance_uuid'])



    def DownloadUploadTest(self,request):
        LOG.info("download upload test starts")
        content = request.get_json()
        LOG.debug(content)
        name = content['service_name']
        vendor = content['service_vendor']
        version = content['service_version']        
        callback = content['callback']
        package_id = self.getVnVPackagebyId(name,vendor,version)        
        download_pkg = self.downloadPackageTGO(package_id)
        download_pkg_json = json.loads(download_pkg)        
        package_path = download_pkg_json['package']        
        upload_pkg = self.uploadPackage(package_path)  
        LOG.debug(upload_pkg)
        return upload_pkg     


    def instantiateService(self,request): 
        LOG.info("instantiate service starts")
        content = request.get_json()
        LOG.debug("instantiateServiceRequest: {}".format(content))
        LOG.debug("instantiateServiceDbType: {}".format(self.authmanager.db_type))
        
        name = content['service_name']
        vendor = content['service_vendor']
        version = content['service_version']        
        callback = content['callback']
        vnv_service_id = None
        package_id = None
        download_pkg = None
        package_path = None
        thing = None
        service_id = None
        upload_pkg = None
        package_uploaded = False

        if self.authmanager.db_type == 'sonata':
            '''
            try:
                vnv_service_id = self.getVnVServiceId(name,vendor,version)
                LOG.debug("this is the service id in the vnv")
                LOG.debug(vnv_service_id)
            except:
                msg = "{\"error\": \"error getting the service from the VnV Catalog\"}"
                return msg 

            try:
                package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)            
                LOG.debug(package_id)
            except:                
                msg = "{\"error\": \"error getting the package from the VnV Catalog\"}"
                LOG.debug(msg)
                return msg 
            
            try:
                download_pkg = self.downloadPackageTGO(package_id)
                LOG.debug(download_pkg)            
                download_pkg_json = json.loads(download_pkg)
            
                download_pkg = self.downloadPackageTGO(package_id)
                download_pkg_json = json.loads(download_pkg)        
                package_path_downloaded = download_pkg_json['package']
            except:
                msg = "{\"error\": \"error downloading the package from the VnV Catalog\"}"
                LOG.debug(msg)
                return msg              
            '''


            ###### commented for try test ffor when the service already exists in the SP
            try:
                service_id = self.getServiceId(name,vendor,version)
                LOG.debug("Getting service ID: {} from vendor: {}, name: {}, version: {}".format(service_id, vendor, name, version))
                if service_id is not None:
                    LOG.debug("The Service is already in the SP")
            except:
                LOG.debug("The Service is not in the SP  ") 

                try:
                    vnv_service_id = self.getVnVServiceId(name,vendor,version)
                    LOG.debug("this is the service id in the vnv")
                    LOG.debug(vnv_service_id)
                except:
                    msg = "{\"error\": \"error getting the service from the VnV Catalog\"}"
                    return msg 

                try:
                    package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)
                    LOG.debug("Package_id: {}".format(package_id))
                except:                
                    msg = "{\"error\": \"error getting the package from the VnV Catalog\"}"
                    LOG.debug(msg)
                    return msg 
                
                try:
                    download_pkg = self.downloadPackageTGO(package_id)
                    LOG.debug(download_pkg)            
                    download_pkg_json = json.loads(download_pkg)
                
                    download_pkg = self.downloadPackageTGO(package_id)
                    download_pkg_json = json.loads(download_pkg)        
                    package_path_downloaded = download_pkg_json['package']
                except:
                    msg = "{\"error\": \"error downloading the package from the VnV Catalog\"}"
                    LOG.debug(msg)
                    return msg 

                upload_pkg = self.uploadPackage(package_path_downloaded)
                time.sleep(7) 
                package_uploaded = True
                LOG.debug("upload package response")
                LOG.debug(upload_pkg)
                upload_pkg_json =  json.loads(upload_pkg)
                upload_pkg_json_process_uuid =  upload_pkg_json['package_process_uuid']
                upload_pkg_status = self.uploadPackageStatus(upload_pkg_json_process_uuid)
                LOG.debug(upload_pkg_status)

                while upload_pkg_status == 'running':
                    upload_pkg_status = self.uploadPackageStatus(upload_pkg_json_process_uuid)                    
                    LOG.debug(upload_pkg_status)
                    if upload_pkg_status == 'running':
                        time.sleep(3)  
                    if upload_pkg_status == 'error':             
                        return "error uploading package"             


            try:
                service_id = self.getServiceId(name,vendor,version)
                LOG.debug(service_id)
            except:
                LOG.error("The service is not in the SP. Was the package uploaded?")

            time.sleep(5)
            try:
                instance_name = content['instance_name']
            except:
                LOG.debug("No instance name found")

            instantiate_str = "{\"service_uuid\": \"" + service_id + "\", \"name\": \"" + instance_name + "\"}"
            LOG.debug(instantiate_str)

            instantiation_call = None
            try:
                instantiation_call = self.instantiation(instantiate_str)  
                LOG.debug(instantiation_call)     
            except:
                msg = "{\"error\": \"error in the instantiation process, check the SP logs\"}"
                return msg  
            
            LOG.debug(instantiation_call)
            try:
                _thread.start_new_thread(self.SonataInstantiateCallback, (callback,instantiation_call,content))
            except:
                msg = "{\"error\": \"error in the instantiation process, callback aborted\"}"
                return msg                 
            '''
            instantiation_call_str = instantiation_call.__str__()
            instantiation_call_str_replaced = instantiation_call_str.replace("'","\"")
            instantiation_call_str_replaced_2 = instantiation_call_str_replaced[1:]

            #package_id = self.getSPPackageIdfromServiceId(service_id)
            string_inicial = "{\"package_id\": \"" + package_id + "\","
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            LOG.debug(string_inicial)

            request_response = string_inicial + instantiation_call_str_replaced_2

            LOG.debug(request_response)   
            return (request_response)	
            '''
            instantiation_call_str = instantiation_call.__str__()
            instantiation_call_str_replaced = instantiation_call_str.replace("'","\"")
            instantiation_call_str_replaced_2 = instantiation_call_str_replaced[1:]
            LOG.debug("Instantiation call: {}".format(instantiation_call_str))
            package_id = self.getSPPackageIdfromServiceId(service_id)
            #string_inicial = "{\"package_id\": \"" + package_id + "\","
            #request_response = string_inicial + instantiation_call_str_replaced_2

            string_inicial = "{\"package_id\": \"" + package_id + "\","            
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")                        
            request_response = string_replaced + instantiation_call_str_replaced_2

            LOG.debug(request_response)   
            return (request_response)            
	

        if self.authmanager.db_type == 'osm':
            LOG.debug("This SP is osm")
            service_id = None
            package_id = "package_id"
            package_path = None
            vnv_service_id = None

            LOG.debug("instantion for osm SPs stars")

            ### package operations

            '''         
            vnv_service_id = self.getVnVOSMServiceId(name,vendor,version)
            package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)            
            LOG.debug(package_id)
            download_pkg = self.downloadPackageTGO(package_id)
            LOG.debug(download_pkg)            
            download_pkg_json = json.loads(download_pkg)
        
            download_pkg = self.downloadPackageTGO(package_id)
            download_pkg_json = json.loads(download_pkg)        
            package_path_downloaded = download_pkg_json['package'] 

            unzip = self.unzipPackage(package_path_downloaded)  

            LOG.debug(unzip)       
            
            #package_path = '/app/packages/' + package_id
            package_path = unzip
            
            #package_path = '/home/luis/Escritorio/cirros/tgos_osm/basic_osm'
            LOG.debug(package_path)
            '''
            

            try:
                service_id = self.getOSMServiceId(name,vendor,version)
                LOG.debug("service_id: {}".format(service_id))
                if service_id == 'error':
                    raise Exception('raising exception') 
            except:
                logging.debug("The Service is not in the SP  ")
                # if the service is not in the SP, we need to upload it

                try:
                    vnv_service_id = self.getVnVOSMServiceId(name,vendor,version)
                    package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)            
                    LOG.debug("Package_id: {}".format(package_id))
                    download_pkg = self.downloadPackageTGO(package_id)
                    LOG.debug("download_pkg: {}".format(download_pkg))            
                    download_pkg_json = json.loads(download_pkg)
                
                    download_pkg = self.downloadPackageTGO(package_id)
                    download_pkg_json = json.loads(download_pkg)        
                    package_path_downloaded = download_pkg_json['package'] 
                except:
                    msg = "{\"error\": \"error getting the service from the VnV Catalog\"}"
                    return msg 

                try:
                    package_path = self.unzipPackage(package_path_downloaded)
                    LOG.debug("package_path: {}".format(package_path))                       
                except:
                    msg = "{\"error\": \"error decompressing the tgo file\"}"
                    return msg 

                functions_array = self.createFunctionsArray(package_path)
                services_array = self.createServicesArray(package_path)
                
                for function in functions_array:
                    function_str = "{\"function\": \"" + function + "\"}"
                    LOG.debug(function_str)                                        
                    function_json = json.loads(function_str.__str__())
                    LOG.debug(function_json)
                    LOG.debug(function_json['function'])
                    function_file_path = function_json['function']

                    try:                   
                        #upload_function = self.uploadOSMFunction(function_file_path)  
                        upload_function = self.uploadOSMFunctionAndFiles(function_file_path,package_path)                     
                        LOG.debug (upload_function)
                        upload_function_str = upload_function
                        LOG.debug (upload_function_str)

                        if upload_function_str.__str__().find('CONFLICT'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg 
                        if upload_function_str.__str__().find('BAD_REQUEST'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg  

                    except:
                        LOG.debug("problem uploading the function to the SP")

                time.sleep(3)
                for service in services_array:
                    service_str = "{\"service\": \"" + service + "\"}"

                    LOG.debug(service_str)                                        
                    service_json = json.loads(service_str.__str__())
                    LOG.debug(service_json)
                    LOG.debug(service_json['service'])
                    service_file_path = service_json['service']

                    try:
                        upload_service = self.uploadOSMService(service_file_path)
                        LOG.debug(upload_service)
                        if upload_service == 'CONFLICT':
                            LOG.debug("This Service is already in the SP")       
                        if upload_service != 'CONFLICT':
                            LOG.debug("This Service is not in the SP")                                   
                            package_uploaded = True
                            service_id = self.getUploadedOSMServiceId(upload_service)
                    except:
                        LOG.debug("problem uploading the service to osm")
                    
                    try:
                        #service_id = self.getUploadedOSMServiceId(upload_service)
                        service_id = self.getOSMServiceId(name,vendor,version)
                        LOG.debug("THIS IS THE NEW UPLOADED SERVICE ID")
                        LOG.debug(service_id)
                        #return service_id
                    except:
                        msg = "{\"error\": \"error getting the service id from the SP Catalog\"}"
                        return msg 
                
                #package_uploaded = True
                
            time.sleep(2)

            nsd_name = service_id

            ns_name = content['instance_name']

            LOG.debug(nsd_name)
            LOG.debug(ns_name)

            instantiate_str = "{\"nsd_name\": \"" + nsd_name + "\", \"ns_name\": \"" + ns_name + "\", \"vim_account\": \"" + self.authmanager.vim_account + "\"}"
            
            instantiation_call = None

            try:
                instantiation_call = self.instantiation(instantiate_str)  
                LOG.debug("instantiation_call: {}".format(instantiation_call))  
            except:
                msg = "{\"error\": \"error instantiating, check the logs\"}"
                return msg 

            _thread.start_new_thread(self.OSMInstantiateCallback, (callback,instantiation_call))

            instantiation_call_str = instantiation_call
            LOG.debug(instantiation_call_str)   
            instantiation_call_json = json.loads(instantiation_call_str)  
            LOG.debug(instantiation_call_json)
            instantiation_id = instantiation_call_json['id']
            LOG.debug(instantiation_id) 

            string_inicial = "{\"package_id\": \"" + package_id + "\","
            #LOG.debug(string_inicial)                                  
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")            
            request_response = string_replaced + "\"id\": \"" + instantiation_id + "\"}"   
  
            LOG.debug(request_response)   
            return (request_response)	            

    def get_request(self, request_uuid):
        LOG.debug("Getting request: {}".format(request_uuid))
        response = requests.get("{}/api/v3/requests/{}".format(self.authmanager.db_host, request_uuid), verify=False)
        LOG.debug("Request: {}".format(response.json()))
        return response.json()

    def SonataInstantiateCallback(self,callback,instantiation_call, content):
        LOG.info("sonata instantiate callback starts")
        LOG.debug(instantiation_call)
        instance_status = None

        try:
            instantiation_request_json_dumps = json.dumps(instantiation_call)
            LOG.debug(instantiation_request_json_dumps)
            instantiation_request_json = json.loads(instantiation_call)
            LOG.debug(instantiation_request_json)
            LOG.debug(instantiation_request_json['id'])
            instantiation_request_id = instantiation_request_json['id']        
            LOG.debug(instantiation_request_id)
            time.sleep(2)
            instance_status = self.wait_for_instantiation(instantiation_request_id)
            instantiation_request_json = self.get_request(instantiation_request_id)
            LOG.debug("Instance Status: {}".format(instance_status))
        except:
            msg = "{\"error\": \"error getting request status\"}"

            msg_str = msg.__str__()
            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  msg_str  +  "' " + callback        
            LOG.debug(callback_post)		
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug(call)	

            return msg  
            

        if instance_status == 'READY':
            instantiation_info = self.instantiationInfoCurator(instantiation_request_id)
            LOG.debug(instantiation_info) 
            instantiation_info_str = instantiation_info.__str__()
            string_replaced = instantiation_info_str.replace("'","\"")        
            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  string_replaced  +  "' " + callback        
            LOG.debug(callback_post)		
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug(call)	

            info_monitoring =self.instantiationInfoMonitoring(instantiation_request_id)	
            LOG.debug(info_monitoring) 
            info_monitoring_str = info_monitoring.__str__()
            monitoring_string_replaced = info_monitoring_str.replace("'","\"")        
            monitoring_callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  monitoring_string_replaced  +  "' " + self.authmanager.mon_url        
            LOG.debug(monitoring_callback_post)		
            call_mon = subprocess.check_output([monitoring_callback_post], shell=True)
            LOG.debug("instantiation_request_json: {}".format(instantiation_request_json))
            instance_uuid = instantiation_request_json.get("instance_uuid")
            LOG.debug("Instance uuid: {}".format(instance_uuid))
            if content.get('policy_id') and instance_uuid:
                LOG.debug("Get_Host_IP: {}".format(self.authmanager.db_host))
                response = requests.get("{}/api/v3/policies/activate/{}/{}".format(self.authmanager.db_host, instance_uuid, content['policy_id']), verify=False)
                LOG.debug("Policy activation result code: {} with text: {}".format(response.status_code, response.text ))


        if instance_status == 'ERROR': 

            inst_error = None 

            instantiation_request_json_dumps = json.dumps(instantiation_call)
            LOG.debug(instantiation_request_json_dumps)
            instantiation_request_json = json.loads(instantiation_call)
            LOG.debug(instantiation_request_json)
            LOG.debug(instantiation_request_json['id'])
            instantiation_request_id = instantiation_request_json['id']        
            LOG.debug(instantiation_request_id)

            time.sleep(2)

            instantiation_request_content = self.getSonataRequest(instantiation_request_id)
            LOG.debug(instantiation_request_content)

            #instantiation_request_content_dumps = json.dumps(instantiation_request_content)
            #LOG.debug(instantiation_request_content_dumps)
            instantiation_request_content_json = json.loads(instantiation_request_content)
            LOG.debug(instantiation_request_content_json)                        

            #inst_error = instantiation_request_content['error'] 
            inst_error = instantiation_request_content_json['error'] 
            #inst_error = self.getRequestError(instantiation_request_id)
            LOG.debug("This is the request error")
            LOG.debug(inst_error)
            error_string = '\"error\": \"' + inst_error + '\"'


            try:
                callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json' --data '{" +  error_string +  "}' " + callback         
                LOG.debug(callback_post)
                call = subprocess.check_output([callback_post], shell=True)
                LOG.debug(call)
            except:
                LOG.debug("Error sending the callback to the curator")

        LOG.info("sonata instantiate callback ends")        

    def getSonataRequest(self,id):    
        LOG.info("instantiation status starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        url = self.authmanager.db_host + ':32002/api/v3/requests/' +  id            
        time.sleep(2)
        LOG.debug(url)
        response = requests.get(url,headers=JSON_CONTENT_HEADER)
        LOG.debug(response) 
        LOG.debug(response.text) 
        response_json = response.content
        LOG.debug(response_json)            
        LOG.debug(response.text)
        return (response.text)



    def instantiateServiceTest(self,request): 
        LOG.info("instantiate service TESTS starts")
        content = request.get_json()        
        LOG.debug(content)
        name = content['service_name']
        vendor = content['service_vendor']
        version = content['service_version']
        policy_id = content.get('policy_id')
        callback = content['callback']
        package_uploaded = False

        service_id = None   
        if self.authmanager.db_type == 'sonata':
               ### service operations
            service_id = self.getServiceId(name,vendor,version)
            LOG.debug("this is the service_id")
            LOG.debug(service_id)
            time.sleep(5)
            try:
                instance_name = content['instance_name']
            except:
                LOG.debug("No instance name found")

            instantiate_str = "{\"service_uuid\": \"" + service_id + "\", \"name\": \"" + instance_name + "\"}"
            LOG.debug(instantiate_str)

            instantiation_call = None
            try:
                instantiation_call = self.instantiation(instantiate_str)  
                LOG.debug(instantiation_call)     
            except:
                msg = "{\"error\": \"error in the instantiation process, check the SP logs\"}"
                return msg  
            
            LOG.debug(instantiation_call)
            _thread.start_new_thread(self.SonataInstantiateCallback, (callback,instantiation_call,content))
            
            instantiation_call_str = instantiation_call.__str__()
            instantiation_call_str_replaced = instantiation_call_str.replace("'","\"")
            instantiation_call_str_replaced_2 = instantiation_call_str_replaced[1:]

            package_id = self.getSPPackageIdfromServiceId(service_id)
            string_inicial = "{\"package_id\": \"" + package_id + "\","
            #request_response = string_inicial + instantiation_call_str_replaced_2

            
            package_uploaded = True
            string_inicial = "{\"package_id\": \"" + package_id + "\","
            
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")                        
            request_response = string_replaced + instantiation_call_str_replaced_2




            LOG.debug(request_response)   
            return (request_response)


        if self.authmanager.db_type == 'osm':
            LOG.debug("This SP is osm")
            service_id = None
            package_id = "package_id"
            package_path = None
            vnv_service_id = None

            LOG.debug("instantion for osm SPs stars")

            

            try:
                service_id = self.getOSMServiceId(name,vendor,version)
                LOG.debug(service_id)
                if service_id == 'error':
                    raise Exception('raising exception') 
            except:
                logging.debug("The Service is not in the SP  ") 
 


                #package_path = '/packages/cirros_osm_sin_cloud_init'
                package_path = '/packages/cirros_osm_juju_charms'
                
                #package_path = '/home/luis/mob'
                LOG.debug(package_path)
                



                
                functions_array = self.createFunctionsArray(package_path)
                LOG.debug(functions_array)                                        

                for function in functions_array:
                    LOG.debug (function)
                    
                    function_str = "{\"function\": \"" + function + "\"}"
                    LOG.debug(function_str)                                        
                    function_json = json.loads(function_str.__str__())
                    LOG.debug(function_json)
                    LOG.debug(function_json['function'])
                    function_file_path = function_json['function']
                    

                    try:                   
                        #upload_function = self.uploadOSMFunction(function_file_path)                     
                        #upload_function = self.uploadOSMFunctionAndFiles(function_file_path,package_path)  
                        upload_function = self.uploadOSMFunctionAndTarFiles(function_file_path,package_path)  

                        LOG.debug (upload_function)
                        LOG.debug ("11111111111111111111111111111111111111111111111111111")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")
                        LOG.debug ("")


                        upload_function_str = upload_function
                        LOG.debug (upload_function_str)

                        if upload_function_str.__str__().find('CONFLICT'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg 
                        if upload_function_str.__str__().find('BAD_REQUEST'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg  

                    except:
                        
                        LOG.debug("problem uploading the function to the SP")
  
                services_array = self.createServicesArray(package_path)
                LOG.debug(services_array)  
                time.sleep(3)
                for service in services_array:
                    service_str = "{\"service\": \"" + service + "\"}"

                    LOG.debug(service_str)                                        
                    service_json = json.loads(service_str.__str__())
                    LOG.debug(service_json)
                    LOG.debug(service_json['service'])
                    service_file_path = service_json['service']

                    try:
                        upload_service = self.uploadOSMService(service_file_path)
                        LOG.debug(upload_service)
                        if upload_service == 'CONFLICT':
                            LOG.debug("This Service is already in the SP")       
                        if upload_service != 'CONFLICT':
                            LOG.debug("This Service is not in the SP")                                   
                            package_uploaded = True
                            service_id = self.getUploadedOSMServiceId(upload_service)
                    except:
                        LOG.debug("problem uploading the service to osm")
                    
                    #service_id = self.getUploadedOSMServiceId(upload_service)
                    service_id = self.getOSMServiceId(name,vendor,version)

                    LOG.debug("THIS IS THE NEW UPLOADED SERVICE ID")
                    LOG.debug(service_id)
                    #return service_id
                
                #package_uploaded = True
                
            time.sleep(2)

            nsd_name = service_id

            ns_name = content['instance_name']

            LOG.debug(nsd_name)
            LOG.debug(ns_name)

            instantiate_str = "{\"nsd_name\": \"" + nsd_name + "\", \"ns_name\": \"" + ns_name + "\", \"vim_account\": \"" + self.authmanager.vim_account + "\"}"
            LOG.debug("THIS IS THE INSTANTIATE STRING FOR OSM")
            LOG.debug("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

            '''
            LOG.debug(instantiate_str)


            LOG.debug("aaaaaaaaaaa")

            instantiation_call = self.instantiation(instantiate_str)    
            LOG.debug(instantiation_call)

            _thread.start_new_thread(self.OSMInstantiateCallback, (callback,instantiation_call))

            instantiation_call_str = instantiation_call
            LOG.debug(instantiation_call_str)   
            instantiation_call_json = json.loads(instantiation_call_str)  
            LOG.debug(instantiation_call_json)
            instantiation_id = instantiation_call_json['id']
            LOG.debug(instantiation_id) 

            string_inicial = "{\"package_id\": \"" + package_id + "\","
            #LOG.debug(string_inicial)                                  
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")            
            request_response = string_replaced + "\"id\": \"" + instantiation_id + "\"}"   
  
            LOG.debug(request_response)   
            return (request_response)	
            '''
            return (instantiate_str)                 
                 

    



    def createServicesArray(self,package_path):
        services_array = None
        files = []
        functions_array = []
        services_array = []
        for r,d,f in os.walk(package_path):
            for file in f:
                    if '.yaml' in file:
                        files.append(os.path.join(r,file))
                    if '.yml' in file:
                        files.append(os.path.join(r,file))                  
        for f in files:
            LOG.debug(f)
            with open(f) as file_in_array:
                    file = yaml.load(file_in_array)      
                    #LOG.debug(file)
                    try:
                        vnfd = file['vnfd:vnfd-catalog']
                        #LOG.debug("this file is an osm vnfd")
                        functions_array.append(f)
                    except:
                        try:
                                nsd = file['nsd:nsd-catalog']
                                #LOG.debug("this file is an osm nsd")
                                services_array.append(f)                  
                        except:
                                LOG.debug("this files is not an OSM vnfd or nsd")
        LOG.debug("osm functions list:")
        for func in functions_array:
            LOG.debug(func)
        LOG.debug("osm services list:")
        for serv in services_array:
            LOG.debug(serv)                
        return services_array



    def getPackageIdfromServiceId (self,service_id):
        LOG.info("get package id from service id starts")
        package_id = None
        msg = ""
        vnv_packages = self.getVnVPackages()
        LOG.debug("VnV packages: {}".format(vnv_packages))
        vnv_packages_json = json.loads(vnv_packages)

        for package in vnv_packages_json:
            LOG.debug("Package uuid: {}".format(package['uuid']))
            package_pd = package['pd']
            package_content = package_pd['package_content']
            LOG.debug("Package content: {}".format(package_content))
            for pc in package_content:
                nsd_uuid = pc['uuid']
                LOG.debug("nsd_uuid: {} == service_id: {}".format(nsd_uuid, service_id))
                if nsd_uuid == service_id:                    
                    package_id = package['uuid']

                    LOG.debug("Package_id: {}".format(package_id))
                    LOG.info("get package id from service id finishing")
                    return package_id, msg
        
        if package_id == None:
            msg = "error getting the id from the packages list"
            return package_id, msg
        

    def backupgetPackageIdfromServiceId (self,service_id):
        LOG.info("get package id from service id starts")
        package_id = None
        correct_package = None
        vnv_packages = self.getVnVPackages()
        vnv_packages_json = json.loads(vnv_packages)
        LOG.debug(vnv_packages_json)        

        for package in vnv_packages_json:
            package_pd = package['pd']
            package_content = package_pd['package_content']
            #LOG.debug(package_content)
            for pc in package_content:
                nsd_uuid = pc['uuid']
                #LOG.debug(nsd_uuid)
                if nsd_uuid == service_id:
                    correct_package = package
        
        package_id = correct_package['uuid']
        LOG.debug(package_id)
        return package_id        


    def getSPPackageIdfromServiceId (self,service_id):
        LOG.info("get sp paclage id from service id starts")
        package_id = None
        correct_package = None
        vnv_packages = self.getPackages()
        LOG.debug(vnv_packages)
        vnv_packages_json = json.loads(vnv_packages)
        LOG.debug(vnv_packages_json)        

        for package in vnv_packages_json:
            LOG.debug(package)
            package_pd = package['pd']
            LOG.debug(package_pd)            
            package_content = package_pd['package_content']
            LOG.debug(package_content)
            
            for pc in package_content:
                nsd_uuid = pc['uuid']
                LOG.debug(nsd_uuid)
                if nsd_uuid == service_id:
                    correct_package = package
        
        package_id = correct_package['uuid']
        LOG.debug(package_id)
        return package_id


    def getPreIntPackages (self):    
        LOG.info("pre int packages starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}
        url = 'http://pre-int-sp-ath.5gtango.eu:32002/api/v3/packages'
        response = requests.get(url, headers=JSON_CONTENT_HEADER)    
        if response.ok:        
            LOG.debug(response.text)
            return (response.text)


    def getVnVServiceId(self,name,vendor,version):    
        LOG.info("get vnv service id starts")
        uuid = None
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}  
        if self.authmanager.db_type == 'sonata':          
            url = 'http://tng-cat:4011/api/catalogues/v2/network-services'  
            response = requests.get(url,headers=JSON_CONTENT_HEADER)
            response_json = response.content
            jjson = json.loads(response_json)
            for x in jjson:
                LOG.debug(x)
                LOG.debug(x)
                try:
                    if ( x['nsd']['name'] == name and x['nsd']['vendor'] == vendor and x['nsd']['version'] == version ) :
                        LOG.debug("this is the correct service")
                        uuid = x['uuid']
                        LOG.debug(uuid)
                        return uuid  
                except:
                    LOG.debug("this descriptor is not a Sonata one")

        LOG.debug(uuid)
        return uuid     

    def getVnVOSMServiceId(self,name,vendor,version):    
        LOG.info("get vnv service id starts")
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
                LOG.debug("OSM service descriptor, checking if is the one we are searching:") 
                if ( x['nsd']['nsd:nsd-catalog']['nsd']['name'] == name and x['nsd']['nsd:nsd-catalog']['nsd']['vendor'] == vendor and x['nsd']['nsd:nsd-catalog']['nsd']['version'] == version ) :
                    LOG.debug("same name")
                    uuid = x['uuid']
                    LOG.debug(uuid)  
            except:
                LOG.debug("this descriptor is not a OSM one")       

        LOG.debug(uuid)
        return uuid    


    def getVnVOSMServiceIdTEST(self,name,vendor,version):    
        LOG.info("get vnv service id starts")
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
                LOG.debug("OSM service descriptor, checking if is the one we are searching:") 
                if ( x['nsd']['nsd:nsd-catalog']['nsd']['name'] == name and x['nsd']['nsd:nsd-catalog']['nsd']['vendor'] == vendor and x['nsd']['nsd:nsd-catalog']['nsd']['version'] == version ) :
                    LOG.debug("same name")
                    uuid = x['uuid']
                    LOG.debug(uuid)  
            except:
                LOG.debug("Sonata services descriptor, trying next")        

        LOG.debug(uuid)
        return uuid          


    def deletePackagefromService(self,name,vendor,version):    
        LOG.info("delete package from service starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   
        response = None        
        if self.authmanager.db_type == 'sonata':    
            try:
                service_id = self.getServiceId(name,vendor,version)
                package_id = self.getSPPackageIdfromServiceId(service_id)            
                url = self.authmanager.db_host + ':32002/api/v3/packages/' + package_id   
                LOG.debug(url)     
                response = requests.delete(url,headers=JSON_CONTENT_HEADER)
                LOG.debug(response)    
        
                LOG.debug(response.text)
                msg = '{\"msg\": \"package deleted\"}'
                LOG.debug(msg)
                return msg
            except:
                msg = "{\"error\": \"error deleting the package in the SP from the service info\"}"
                return msg              
        

    

        
    def instantiationDeleteTest(self,request):    
        LOG.info("instantiation delete TESTS starts")
        JSON_CONTENT_HEADER = {'Content-Type':'application/json'}   

        if self.authmanager.db_type == 'sonata':
            url = self.authmanager.db_host + ':32002/api/v3/requests'
            LOG.debug(url)
            LOG.debug(request)            
            #LOG.debug(request)
            #LOG.debug(type(request))
            
            content = json.loads(request)
            instance_uuid = content['instance_uuid']    
            LOG.debug(instance_uuid)
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)

            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
            
            LOG.debug(terminate_str)            
            delete_ns = "curl -s -X POST --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -d '" + terminate_str + "' " + url
            LOG.debug(delete_ns)
            terminate = subprocess.check_output([delete_ns], shell=True)
            LOG.debug(terminate)

            LOG.debug(terminate)

            content = json.loads(request)
            ns_id = content['instance_uuid']
            LOG.debug(ns_id)
            '''
            url_monitoring = self.getMonitoringURLs()
            terminate_string = "curl -s -X DELETE -H \"Content-type: application/json\" "  + url_monitoring + "/" + ns_id 
            LOG.debug(terminate_string)   
            try: 
                terminate_monitoring = subprocess.check_output([terminate_string], shell=True)
                LOG.debug(terminate_monitoring)
            except:
                LOG.debug(terminate_monitoring)
            '''

            # deleting the descriptors
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)
            if ( package_uploaded == True ) or ( package_uploaded == "true" ) or ( package_uploaded == "True" ):
                LOG.debug(ns_id)
                try:
                    LOG.debug(ns_id)
                    instance_status = self.SonataTerminateStatus(ns_id)
                    LOG.debug(instance_status)
                    while instance_status == 'normal operation':
                        time.sleep(5)
                        instance_status = self.SonataTerminateStatus(ns_id)      
                        LOG.debug(instance_status)  
                    descriptor_reference_id = self.SonataTerminateDescriptorReference(ns_id)
                    LOG.debug(descriptor_reference_id)
                    name = self.SonataTerminateDescriptorName(descriptor_reference_id)
                    LOG.debug(name)
                    vendor = self.SonataTerminateDescriptorVendor(descriptor_reference_id)
                    LOG.debug(vendor)
                    version = self.SonataTerminateDescriptorVersion(descriptor_reference_id)
                    LOG.debug(version)
                    delete_descriptors = self.deletePackagefromService(name,vendor,version)                
                    LOG.debug(delete_descriptors) 
                except:
                    LOG.debug("error trying to delte the tgo from the SP")

            LOG.debug(terminate)
            return terminate

        if self.authmanager.db_type == 'osm':
            LOG.debug(request)
            token = self.__getOSMToken(request)
            LOG.debug(token)

            url = self.authmanager.db_host + ':9999/osm/nslcm/v1/ns_instances_content'
            url_2 = url.replace("http","https")
            
            content = json.loads(request)
            ns_id = content['instance_uuid']
            LOG.debug(ns_id)
                        
            LOG.debug(ns_id)
            delete_ns = "curl -s -X DELETE --insecure -H \"Content-type: application/json\"  -H \"Accept: application/json\" -H \"Authorization: Bearer "
            delete_ns_2 = delete_ns +token + "\" "
            delete_ns_3 = delete_ns_2 + " " + url_2 + "/" + ns_id          
            LOG.debug(delete_ns_3)
            # terminating the instance
            terminate = subprocess.check_output([delete_ns_3], shell=True)
            # deleting the descriptors
            package_uploaded = content['package_uploaded']
            LOG.debug(package_uploaded)
            if ( package_uploaded == True ) or ( package_uploaded == "true" ) or ( package_uploaded == "True" ):
                instance_status = self.OSMTerminateStatus(url_2,ns_id)
                LOG.debug(instance_status)
                while instance_status != 'terminated':
                    time.sleep(2)
                    instance_status = self.OSMTerminateStatus(url_2,ns_id)
                delete_descriptors = self.deleteOSMDescriptors(ns_id)                
                LOG.debug(delete_descriptors)

            LOG.debug(terminate)
            #_thread.start_new_thread(self.OSMUploadServiceCallback, (token,url_2,callback_url,content['ns_id']))
                                 
            LOG.debug(terminate)
            return (terminate)         

    def delPackageSonata (self,ns_id):
        LOG.debug(ns_id)
        instance_status = self.SonataTerminateStatus(ns_id)
        LOG.debug(instance_status)
        while instance_status == 'normal operation':
            time.sleep(5)
            instance_status = self.SonataTerminateStatus(ns_id)      
            LOG.debug(instance_status)  
        descriptor_reference_id = self.SonataTerminateDescriptorReference(ns_id)
        LOG.debug(descriptor_reference_id)
        name = self.SonataTerminateDescriptorName(descriptor_reference_id)
        LOG.debug(name)
        vendor = self.SonataTerminateDescriptorVendor(descriptor_reference_id)
        LOG.debug(vendor)
        version = self.SonataTerminateDescriptorVersion(descriptor_reference_id)
        LOG.debug(version)
        delete_descriptors = self.deletePackagefromService(name,vendor,version)                
        LOG.debug(delete_descriptors)  
              


    def instantiateServiceRemoteTest(self,request): 
        LOG.info("instantiate service starts")
        content = request.get_json()
        LOG.debug(content)
        name = content['service_name']
        vendor = content['service_vendor']
        version = content['service_version']        
        callback = content['callback']
        vnv_service_id = None
        package_id = None
        download_pkg = None
        package_path = None
        thing = None
        service_id = None
        upload_pkg = None
        package_uploaded = False

        if self.authmanager.db_type == 'sonata':
            ###### commented for try test ffor when the service already exists in the SP
            try:
                service_id = self.getServiceId(name,vendor,version)
                if service_id is not None:
                    LOG.debug("The Service is already in the SP")
            except:
                LOG.debug("The Service is not in the SP  ") 

                try:
                    vnv_service_id = self.getVnVServiceId(name,vendor,version)
                    LOG.debug("this is the service id in the vnv")
                    LOG.debug(vnv_service_id)
                except:
                    msg = "{\"error\": \"error getting the service from the VnV Catalog\"}"
                    return msg 

                try:
                    package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)            
                    LOG.debug("Package_id: {}".format(package_id))
                except:                
                    msg = "{\"error\": \"error getting the package from the VnV Catalog\"}"
                    LOG.debug(msg)
                    return msg 
                
                try:
                    download_pkg = self.downloadPackageTGO(package_id)
                    LOG.debug(download_pkg)            
                    download_pkg_json = json.loads(download_pkg)
                
                    download_pkg = self.downloadPackageTGO(package_id)
                    download_pkg_json = json.loads(download_pkg)        
                    package_path_downloaded = download_pkg_json['package']
                except:
                    msg = "{\"error\": \"error downloading the package from the VnV Catalog\"}"
                    LOG.debug(msg)
                    return msg 

                upload_pkg = self.uploadPackage(package_path_downloaded)
                time.sleep(7) 
                package_uploaded = True
                LOG.debug("upload package response")
                LOG.debug(upload_pkg)
                upload_pkg_json =  json.loads(upload_pkg)
                upload_pkg_json_process_uuid =  upload_pkg_json['package_process_uuid']
                upload_pkg_status = self.uploadPackageStatus(upload_pkg_json_process_uuid)
                LOG.debug(upload_pkg_status)

                while upload_pkg_status == 'running':
                    upload_pkg_status = self.uploadPackageStatus(upload_pkg_json_process_uuid)                    
                    LOG.debug(upload_pkg_status)
                    if upload_pkg_status == 'running':
                        time.sleep(3)  
                    if upload_pkg_status == 'error':             
                        return "error uploading package"             


            try:
                service_id = self.getServiceId(name,vendor,version)
                LOG.debug(service_id)
            except:
                LOG.error("The service is not in the SP. Was the package uploaded?")

            time.sleep(5)
            try:
                instance_name = content['instance_name']
            except:
                LOG.debug("No instance name found")

            instantiate_str = "{\"service_uuid\": \"" + service_id + "\", \"name\": \"" + instance_name + "\"}"
            LOG.debug(instantiate_str)

            instantiation_call = None
            try:
                instantiation_call = self.instantiation(instantiate_str)  
                LOG.debug(instantiation_call)     
            except:
                msg = "{\"error\": \"error in the instantiation process, check the SP logs\"}"
                return msg  
            
            LOG.debug(instantiation_call)
            try:
                _thread.start_new_thread(self.SonataInstantiateCallbackTest, (callback,instantiation_call))
            except:
                msg = "{\"error\": \"error in the instantiation process, callback aborted\"}"
                return msg                 


            instantiation_call_str = instantiation_call.__str__()
            instantiation_call_str_replaced = instantiation_call_str.replace("'","\"")
            instantiation_call_str_replaced_2 = instantiation_call_str_replaced[1:]

            package_id = self.getSPPackageIdfromServiceId(service_id)


            string_inicial = "{\"package_id\": \"" + package_id + "\","            
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")                        
            request_response = string_replaced + instantiation_call_str_replaced_2




            LOG.debug(request_response)   
            return (request_response)            
	

        if self.authmanager.db_type == 'osm':
            LOG.debug("This SP is osm")
            service_id = None
            package_id = "package_id"
            package_path = None
            vnv_service_id = None

            LOG.debug("instantion for osm SPs stars")

            ### package operations
        
            try:
                service_id = self.getOSMServiceId(name,vendor,version)
                LOG.debug(service_id)
                if service_id == 'error':
                    raise Exception('raising exception') 
            except:
                logging.debug:("The Service is not in the SP  ") 
                # if the service is not in the SP, we need to upload it


                vnv_service_id = self.getVnVOSMServiceId(name,vendor,version)
                package_id, msg = self.getPackageIdfromServiceId(vnv_service_id)    
                LOG.debug("Package_id: {}".format(package_id))
                download_pkg = self.downloadPackageTGO(package_id)
                LOG.debug(download_pkg)            
                download_pkg_json = json.loads(download_pkg)
            
                download_pkg = self.downloadPackageTGO(package_id)
                download_pkg_json = json.loads(download_pkg)        
                package_path_downloaded = download_pkg_json['package'] 

                unzip = self.unzipPackage(package_path_downloaded)  

                LOG.debug(unzip)       
                
                #package_path = '/app/packages/' + package_id
                package_path = unzip
                
                #package_path = '/home/luis/Escritorio/cirros/tgos_osm/basic_osm'
                LOG.debug(package_path)




                functions_array = self.createFunctionsArray(package_path)
                services_array = self.createServicesArray(package_path)
                
                for function in functions_array:
                    function_str = "{\"function\": \"" + function + "\"}"
                    LOG.debug(function_str)                                        
                    function_json = json.loads(function_str.__str__())
                    LOG.debug(function_json)
                    LOG.debug(function_json['function'])
                    function_file_path = function_json['function']

                    try:                   
                        #upload_function = self.uploadOSMFunction(function_file_path)  
                        #upload_function = self.uploadOSMFunctionAndFiles(function_file_path,package_path) 
                        upload_function = self.uploadOSMFunctionAndTarFiles(function_file_path,package_path)                      
                        LOG.debug (upload_function)
                        upload_function_str = upload_function
                        LOG.debug (upload_function_str)

                        if upload_function_str.__str__().find('CONFLICT'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg 
                        if upload_function_str.__str__().find('BAD_REQUEST'):
                            upload_function_str_json = json.loads(upload_function_str)
                            LOG.debug (upload_function_str_json['detail'])
                            msg = "{\"error\": \"" + upload_function_str_json['detail'] + "\"}"
                            return msg  

                    except:
                        LOG.debug("problem uploading the function to the SP")

                time.sleep(3)
                for service in services_array:
                    service_str = "{\"service\": \"" + service + "\"}"

                    LOG.debug(service_str)                                        
                    service_json = json.loads(service_str.__str__())
                    LOG.debug(service_json)
                    LOG.debug(service_json['service'])
                    service_file_path = service_json['service']

                    try:
                        upload_service = self.uploadOSMService(service_file_path)
                        LOG.debug(upload_service)
                        if upload_service == 'CONFLICT':
                            LOG.debug("This Service is already in the SP")       
                        if upload_service != 'CONFLICT':
                            LOG.debug("This Service is not in the SP")                                   
                            package_uploaded = True
                            service_id = self.getUploadedOSMServiceId(upload_service)
                    except:
                        LOG.debug("problem uploading the service to osm")
                    
                    #service_id = self.getUploadedOSMServiceId(upload_service)
                    service_id = self.getOSMServiceId(name,vendor,version)

                    LOG.debug("THIS IS THE NEW UPLOADED SERVICE ID")
                    LOG.debug(service_id)
                    #return service_id
                
                #package_uploaded = True
                
            time.sleep(2)

            nsd_name = service_id

            ns_name = content['instance_name']

            LOG.debug(nsd_name)
            LOG.debug(ns_name)

            instantiate_str = "{\"nsd_name\": \"" + nsd_name + "\", \"ns_name\": \"" + ns_name + "\", \"vim_account\": \"" + self.authmanager.vim_account + "\"}"
            LOG.debug("THIS IS THE INSTANTIATE STRING FOR OSM")
            LOG.debug("aaaaaaaaaaa")

            
            LOG.debug(instantiate_str)


            LOG.debug("aaaaaaaaaaa")

            instantiation_call = self.instantiation(instantiate_str)    
            LOG.debug(instantiation_call)

            _thread.start_new_thread(self.OSMInstantiateCallback, (callback,instantiation_call))

            instantiation_call_str = instantiation_call
            LOG.debug(instantiation_call_str)   
            instantiation_call_json = json.loads(instantiation_call_str)  
            LOG.debug(instantiation_call_json)
            instantiation_id = instantiation_call_json['id']
            LOG.debug(instantiation_id) 

            string_inicial = "{\"package_id\": \"" + package_id + "\","
            #LOG.debug(string_inicial)                                  
            string_inicial = string_inicial + "\"package_uploaded\" : \"" + package_uploaded.__str__() + "\","
            if package_uploaded == True:
                string_replaced = string_inicial.replace("\"True\"","true")                            
            if package_uploaded == False:
                string_replaced = string_inicial.replace("\"False\"","false")            
            request_response = string_replaced + "\"id\": \"" + instantiation_id + "\"}"   
  
            LOG.debug(request_response)   
            return (request_response)	                

    def SonataInstantiateCallbackTest (self,callback,instantiation_call):
        LOG.info("sonata instantiate callback starts")
        LOG.debug(instantiation_call)
        instance_status = None

        try:
            instantiation_request_json_dumps = json.dumps(instantiation_call)
            LOG.debug(instantiation_request_json_dumps)
            instantiation_request_json = json.loads(instantiation_call)
            LOG.debug(instantiation_request_json)
            LOG.debug(instantiation_request_json['id'])
            instantiation_request_id = instantiation_request_json['id']        
            LOG.debug(instantiation_request_id)
            time.sleep(2)
            instance_status = self.wait_for_instantiation(instantiation_request_id)
            LOG.debug(instance_status)
        except:
            msg = "{\"error\": \"error getting request status\"}"

            msg_str = msg.__str__()
            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  msg_str  +  "' " + callback        
            LOG.debug(callback_post)		
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug(call)	

            return msg  
            

        if instance_status == 'READY':
            instantiation_info = self.instantiationInfoCurator(instantiation_request_id)
            LOG.debug(instantiation_info) 
            instantiation_info_str = instantiation_info.__str__()
            string_replaced = instantiation_info_str.replace("'","\"")        
            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  string_replaced  +  "' " + callback        
            LOG.debug(callback_post)		
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug(call)	

            info_monitoring =self.instantiationInfoMonitoring(instantiation_request_id)	
            LOG.debug(info_monitoring) 
            info_monitoring_str = info_monitoring.__str__()
            monitoring_string_replaced = info_monitoring_str.replace("'","\"")        
            monitoring_callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '" +  monitoring_string_replaced  +  "' " + self.authmanager.mon_url        
            LOG.debug(monitoring_callback_post)		
            call_mon = subprocess.check_output([monitoring_callback_post], shell=True)            



        if instance_status == 'ERROR': 

            inst_error = None 

            instantiation_request_json_dumps = json.dumps(instantiation_call)
            LOG.debug(instantiation_request_json_dumps)
            instantiation_request_json = json.loads(instantiation_call)
            LOG.debug(instantiation_request_json)
            LOG.debug(instantiation_request_json['id'])
            instantiation_request_id = instantiation_request_json['id']        
            LOG.debug(instantiation_request_id)
            time.sleep(2)

            inst_error = self.getRequestError(instantiation_request_id)
            LOG.debug("This is the request error")
            LOG.debug(inst_error)

            callback_post = "curl -s -X POST --insecure -H 'Content-type: application/json'" + " --data '{\"error\": \"" + inst_error + "\"}' " + callback        
            LOG.debug(callback_post)
            call = subprocess.check_output([callback_post], shell=True)
            LOG.debug(call)
            
        LOG.info("sonata instantiate callback ends")  


    def getSPIp(self):        
        LOG.info("get sp ip starts")
            
        ping_string = "getent ahostsv4 " + self.authmanager.db_host + " | awk '{print $1}' | head -1"
        LOG.debug(ping_string)
        ip = subprocess.check_output([ping_string], shell=True)
        LOG.debug(ip)       
        ip_decoded = ip.decode('utf-8', 'ignore')    
        LOG.debug (ip_decoded) 
        ip_decoded_replaced = ip_decoded.strip()         
        return ip_decoded_replaced  