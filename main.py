#!/usr/bin/python

from flask import Flask, request, jsonify, render_template
import os, sys, logging, json, argparse 
from configparser import ConfigParser
import requests
from adapters import adapter as adapter
from adapters.serviceplatform import ServicePlatform
from models import utils
from models import users
import psycopg2
#from validator_collection import validators, checkers
import validators


from logger import TangoLogger as TangoLogger

app = Flask(__name__)



LOG = TangoLogger.getLogger(__name__, log_level=logging.DEBUG, log_json=True)
TangoLogger.getLogger("your_module:main", logging.DEBUG, log_json=True)
LOG.setLevel(logging.DEBUG)
#LOG.info("Hello world.")

##### SERVICE PLATFORMS ROUTES #####
@app.route('/service_platforms/count', methods=['GET'])
def countSPs():
    sp = ServicePlatform()
    return sp.countServicePlatforms()
    

@app.route('/service_platforms', methods=['GET','POST','OPTIONS','DELETE','PATCH'])
def sps():
    if request.method == 'GET':
        sp = ServicePlatform()
        return sp.getServicePlatforms()

    if request.method == 'POST':
        msg = {}
        LOG.debug("Request: {}".format(request.is_json))
        vim_account = None
        content = request.get_json()

        is_url = validators.url(content['host'])
        if not is_url:
            LOG.debug("The host provided is not valid")
            msg['error'] = "The host provided is not valid. Format: 'http://<sp_ip>'"
            return msg, 400

        try:
            vim_account = content['vim_account']
        except:
            vim_account = "vim_account"
        
        LOG.debug(content)  
        try:      
            mon_urls = 'http://son-vnv-monitor-manager:8000/api/v2/services'
            LOG.debug("mon_url exists")
            try:
                pr = content['project_name']
                LOG.debug("project name exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],content['project_name'],vim_account,"service_token",mon_urls)
                return sp.registerServicePlatform()
            except:
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],"project_name",vim_account,"service_token",mon_urls)
                return sp.registerServicePlatform()
        except:
            LOG.debug("mon_url does not exists")
            try:
                pr = content['project_name']
                LOG.debug("project name exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],content['project_name'],vim_account,"service_token",mon_urls)
                return sp.registerServicePlatform() 
            except:
                LOG.debug("project name does not exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],"project_name",vim_account,"service_token",mon_urls)
                return sp.registerServicePlatform()         

    if request.method == 'OPTIONS':
        return "Options", 200
    
    if request.method == 'DELETE':        
        return "delete", 200

    if request.method == 'PATCH':    
        content = request.get_json()
        LOG.debug("PATCH_SP: {}".format(content))
        try:      
            mon_urls = content['monitoring_urls']
            LOG.debug("mon_url exists")
            try:
                pr = content['project_name']
                LOG.debug("project name exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],content['project_name'],vim_account,"service_token","http://son-vnv-monitor-manager:8000/api/v2/services")
                return sp.patchServicePlatform()
            except:
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],"project_name",vim_account,"service_token","http://son-vnv-monitor-manager:8000/api/v2/services")
                return sp.patchServicePlatform()
        except:
            LOG.debug("mon_url does not exists")
            try:
                pr = content['project_name']
                LOG.debug("project name exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],content['project_name'],vim_account,"service_token","http://son-vnv-monitor-manager:8000/api/v2/services")
                return sp.patchServicePlatform() 
            except:
                LOG.debug("project name does not exists")
                sp = ServicePlatform(content['name'],content['host'],content['type'],content['username'],content['password'],"project_name",vim_account,"service_token","http://son-vnv-monitor-manager:8000/api/v2/services")
                return sp.patchServicePlatform() 



@app.route('/service_platforms/<service_platform>', methods=['GET','DELETE','PATCH'])
def sp(service_platform):
    if request.method == 'GET':
        sp = ServicePlatform(service_platform,"host","type","username","password","project_name","vim_account","service_token","monitoring_urls")
        return sp.getServicePlatform() 
    if request.method == 'DELETE':          
        sp = ServicePlatform(service_platform,"host","type","username","password","project_name","vim_account","service_token","monitoring_urls")
        return sp.deleteServicePlatform()
    if request.method == 'PATCH':    
        LOG.debug(request.is_json)
        content = request.get_json()
        LOG.debug("PATCH_SP: {}".format(content))

        old_sp = ServicePlatform(service_platform,"host","type","username","password","project_name","vim_account","service_token","monitoring_urls")
        old_sp_response =  old_sp.getServicePlatform()         
        old_sp_content = json.loads(old_sp_response[0])

        try:
            host = content['host']
        except:
            host = old_sp_content['host']
        try:
            username = content['username']
        except:
            username = old_sp_content['username']
        try:
            password = content['password']
        except:
            password = old_sp_content['password']
        try:
            vim_account = content['vim_account']
        except:
            vim_account = old_sp_content['vim_account']    
        try:
            monitoring_urls = content['monitoring_urls']
        except:
            monitoring_urls = old_sp_content['monitoring_urls']

        sp = ServicePlatform(service_platform,host,old_sp_content['type'],username,password,old_sp_content['project_name'],vim_account,old_sp_content['service_token'],monitoring_urls)
        return sp.patchServicePlatform()


##### ADAPTER GENERIC ROUTES #####

@app.route('/adapters/<service_platform>/get_username')
def adapter_get_username(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getDBUserName()

@app.route('/adapters/<service_platform>/get_monitoring_urls')
def adapter_get_monitoring_urls(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getMonitoringURLs()    
 
@app.route('/adapters/<service_platform>/get_password')
def adapter_get_password(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getDBPassword() 

@app.route('/adapters/<service_platform>/get_type')
def adapter_get_type(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getDBType()

@app.route('/adapters/<service_platform>/get_project_name')
def adapter_get_project_name(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getDBProjectName()    

@app.route('/adapters/<service_platform>/get_host')
def adapter_get_host(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getHostIp()

@app.route('/adapters/<service_platform>/get_vim_account')
def adapter_get_vim_account(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getVimAccount()    
  

@app.route('/adapters/<service_platform>/services', methods=['GET'])
def adapter_get_services(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getServices()
    #return ad.getDBType()
   

@app.route('/adapters/<service_platform>/functions', methods=['GET'])
def adapter_get_Functions(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getFunctions()  


@app.route('/adapters/packages/unzip-package', methods=['POST'])
def adapter_unzip_package():
    content = request.get_json()
    LOG.debug(content)
    ad = adapter.Adapter("service_platform")   
    return ad.unzipPackage(content['package']) 



@app.route('/adapters/<service_platform>/services/<name>/<vendor>/<version>', methods=['GET'])
def adapter_get_service(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getService(name,vendor,version)   

@app.route('/adapters/<service_platform>/services/<name>/<vendor>/<version>/id', methods=['GET'])
def adapter_get_service_id(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getServiceId(name,vendor,version)      

@app.route('/adapters/<service_platform>/services/<name>/<vendor>/<version>/instantiations', methods=['GET'])
def adapter_get_service_instantiations(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getServiceInstantiations(name,vendor,version)       


@app.route('/adapters/<service_platform>/packages/<name>/<vendor>/<version>/id', methods=['GET'])
def adapter_get_package_id(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getPackageId(name,vendor,version) 

@app.route('/adapters/<service_platform>/packages/<pkg_id>/package-file', methods=['GET'])
def adapter_get_package_file(service_platform, pkg_id):
    ad = adapter.Adapter(service_platform)
    return ad.getPackageFile(pkg_id)   

@app.route('/adapters/<service_platform>/packages/status/<pkg_process_id>', methods=['GET'])
def upload_package_status(service_platform, pkg_process_id):
    ad = adapter.Adapter(service_platform)
    return ad.uploadPackageStatus(pkg_process_id)   




@app.route('/adapters/<service_platform>/packages', methods=['GET'])
def adapter_get_packages(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.getPackages()

@app.route('/adapters/packages', methods=['GET'])
def adapter_get_vnv_packages():
    ad = adapter.Adapter("service_platform")
    return ad.getVnVPackages()   

@app.route('/adapters/packages/<name>/<vendor>/<version>/id', methods=['GET'])
def adapter_get_vnv_package_by_id(name,vendor, version):
    ad = adapter.Adapter("service_platform")
    return ad.getVnVPackagebyId(name,vendor,version)  

@app.route('/adapters/<service_platform>/packages/<name>/<vendor>/<version>', methods=['GET'])
def adapter_get_package(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getPackage(name,vendor,version)    

@app.route('/adapters/services/<name>/<vendor>/<version>', methods=['GET'])
def adapter_get_services_osm_test(name,vendor, version):
    ad = adapter.Adapter("service_platform")
    return ad.getVnVOSMServiceIdTEST(name,vendor,version)       

#@app.route('/adapters/<service_platform>/packages/<name>/<vendor>/<version>', methods=['DELETE'])
#def adapter_delete_package(service_platform,name,vendor, version):
#    ad = adapter.Adapter(service_platform)
#    return ad.deletePackage(name,vendor,version)   
@app.route('/adapters/<service_platform>/packages/<name>/<vendor>/<version>', methods=['DELETE'])
def adapter_delete_package(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)    
    return ad.deletePackagefromService(name,vendor,version)

@app.route('/adapters/<service_platform>/packages/<name>/<vendor>/<version>/id', methods=['GET'])
def adapter_get_package_by_id(service_platform,name,vendor, version):
    ad = adapter.Adapter(service_platform)
    return ad.getPackagebyId(name,vendor,version)  
    

@app.route('/adapters/<service_platform>/packages', methods=['POST'])
def adapter_upload_package(service_platform):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)
    ad = adapter.Adapter(service_platform)  
    LOG.debug(ad.name)         
    return ad.uploadPackage(content['package'])


@app.route('/adapters/packages/<package_id>/download', methods=['GET'])
def adapter_download_package(package_id):
    ad = adapter.Adapter("service_platform")   
    return ad.downloadPackageTGO(package_id) 
	    

#### SERVICES OPERATIONS #### 
@app.route('/adapters/<service_platform>/instantiations', methods=['GET'])
def serviceInstantiationsGetStatus(service_platform):
    ad = adapter.Adapter(service_platform)
    return ad.instantiationsStatus() 
 
   
@app.route('/adapters/<service_platform>/instantiations/<id>', methods=['GET'])
def serviceInstantiationGetStatus(service_platform,id):
    ad = adapter.Adapter(service_platform)
    return ad.instantiationStatus(id)

@app.route('/adapters/<service_platform>/instantiations/<id>/monitoring', methods=['GET'])
def serviceInstantiationInfoMonitoring(service_platform,id):
    ad = adapter.Adapter(service_platform)
    return ad.instantiationInfoMonitoring(id)  

@app.route('/adapters/<service_platform>/instantiations/<id>/monitoring/tests', methods=['GET'])
def serviceInstantiationInfoMonitoringTest(service_platform,id):
    ad = adapter.Adapter(service_platform)
    return ad.instantiationInfoMonitoringTest(id)     

@app.route('/adapters/<service_platform>/instantiations/<id>/curator', methods=['GET'])
def serviceInstantiationInfoCurator(service_platform,id):
    ad = adapter.Adapter(service_platform)
    return ad.instantiationInfoCurator(id) 


@app.route('/adapters/<service_platform>/instantiations/<id>/ips', methods=['GET'])
def OSMInstantiationGetIPs(service_platform,id):
    ad = adapter.Adapter(service_platform)
    return ad.osmInstantiationIPs(id)


@app.route('/adapters/<service_platform>/instantiations', methods=['POST'])
def serviceInstantiation(service_platform):
    content = request.get_json()
    LOG.debug("service_uuid : "+content['service_uuid'])
    service_uuid = content['service_uuid']
    instantiate_str = "{\"service_uuid\": \"" + service_uuid + "\"}" 
    ad = adapter.Adapter(service_platform)      
    return ad.instantiation(instantiate_str)

@app.route('/adapters/<service_platform>/instantiations/terminate', methods=['POST'])
def serviceterminate(service_platform): 
    LOG.debug(request)
    LOG.debug(type(request))
    content = request.get_json()
    try:         
        LOG.debug(content)
        LOG.debug(content['instance_uuid'])
        instance_uuid = content['instance_uuid']    
        LOG.debug(instance_uuid)
        package_uploaded = content['package_uploaded']
        LOG.debug(package_uploaded)

        if ( package_uploaded == False ) or ( package_uploaded == "false" ):
            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"package_uploaded\": \"False\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
        if ( package_uploaded == True ) or ( package_uploaded == "true" ):
            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"package_uploaded\": \"True\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
        
        LOG.debug(terminate_str)                      
        ad = adapter.Adapter(service_platform)  
        return ad.instantiationDelete(terminate_str)  
            
    except:
        error = "{\"error\": \"error launching the terminate\"}"
        return error

@app.route('/adapters/<service_platform>/instantiations/terminate/tests', methods=['POST'])
def serviceterminatetest(service_platform): 
    LOG.debug(request)
    LOG.debug(type(request))
    content = request.get_json()
    try:         
        LOG.debug(content)
        LOG.debug(content['instance_uuid'])
        instance_uuid = content['instance_uuid']    
        LOG.debug(instance_uuid)
        package_uploaded = content['package_uploaded']
        LOG.debug(package_uploaded)

        if ( package_uploaded == False ) or ( package_uploaded == "false" ):
            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"package_uploaded\": \"False\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
        if ( package_uploaded == True ) or ( package_uploaded == "true" ):
            terminate_str = "{\"instance_uuid\": \"" + instance_uuid + "\",\"package_uploaded\": \"True\",\"sla_id\": \"\",\"request_type\":\"TERMINATE_SERVICE\"}"
        
        LOG.debug(terminate_str)                      
        ad = adapter.Adapter(service_platform)  
        return ad.instantiationDeleteTest(terminate_str)    
        
    except:
        error = "{\"error\": \"error launching the terminate\"}"
        return error




@app.route('/adapters/<service_platform>/instantiations/<service_id>', methods=['GET'])
def serviceInstantiationStatus(service_platform,service_id):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)    
    ad = adapter.Adapter(service_platform)
    #LOG.debug(content['service_uuid'])        
    return ad.instantiationStatus(service_id)      




@app.route('/adapters/<service_platform>/instantiations/delete', methods=['POST'])
def serviceInstantiationDelete(service_platform):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)    
    ad = adapter.Adapter(service_platform)
    #LOG.debug(content['service_uuid'])        
    return ad.instantiationDelete(request)      

@app.route('/adapters/<service_platform>/vims', methods=['GET'])
def getVims(service_platform):
    ad = adapter.Adapter(service_platform)      
    return ad.getVims()  

@app.route('/adapters/<service_platform>/vims/<vim_name>', methods=['GET'])
def getVimInfo(service_platform,vim_name):
    ad = adapter.Adapter(service_platform)      
    return ad.getVim(vim_name)    

@app.route('/adapters/<service_platform>/wims', methods=['GET'])
def getWims(service_platform):
    ad = adapter.Adapter(service_platform)      
    return ad.getWims()  

@app.route('/adapters/<service_platform>/wims/<wim_name>', methods=['GET'])
def getWimInfo(service_platform,wim_name):
    ad = adapter.Adapter(service_platform)      
    return ad.getWim(wim_name)      

    
##### OSM specific endpoints ####
@app.route('/adapters/<service_platform>/get_token', methods=['GET'])
def adapter_osm_get_token(service_platform):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content) 
    ad = adapter.Adapter(service_platform)   
    my_type = ad.getDBType()
    if my_type == 'sonata':
        LOG.debug("this SP is a sonata")
        return ad.getSonataToken(request)    
    if my_type == 'osm':
        return ad.getOSMToken(request)   
       


@app.route('/adapters/<service_platform>/services', methods=['POST'])
def adapter_upload_service(service_platform):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)
    ad = adapter.Adapter(service_platform)  
    LOG.debug(ad.name)         
    return ad.uploadOSMService(request)       


@app.route('/adapters/<service_platform>/functions', methods=['POST'])
def adapter_upload_function(service_platform):
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)
    ad = adapter.Adapter(service_platform)  
    LOG.debug(ad.name)         
    return ad.uploadOSMFunction(request)  

@app.route('/adapters/<service_platform>/functions/<id_to_delete>/delete', methods=['DELETE'])
def adapter_delete_function(service_platform,id_to_delete):
    ad = adapter.Adapter(service_platform)  
    return ad.deleteOSMFunction(id_to_delete)    

@app.route('/adapters/<service_platform>/services/<id_to_delete>/delete', methods=['DELETE'])
def adapter_delete_service(service_platform,id_to_delete):
    ad = adapter.Adapter(service_platform)  
    return ad.deleteOSMService(id_to_delete)  

@app.route('/callback_tests', methods=['POST'])
def adapter_callback_tests():      
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)
    return content.__str__()

@app.route('/adapters/<service_platform>/monitoring', methods=['GET'])
def monitoring_tests(service_platform):        
    ad = adapter.Adapter(service_platform)  
    return ad.monitoringTests("cpu_utilization")  

@app.route('/adapters/policies', methods=['GET'])
def get_policies():        
    sp = ServicePlatform()
    return jsonify(sp.get_policies_sonata())

@app.route('/adapters/<service_platform>/monitoring', methods=['POST'])
def monitoring(service_platform):  
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content)      
    ad = adapter.Adapter(service_platform)  
    return ad.monitoringTests(content['metric'])
    
@app.route('/adapters/instantiate_service', methods=['POST'])
def adapter_instatiate_service():
    LOG.info("start /adapters/instantiate_service")
    content = request.get_json()
    LOG.info("adapter_instatiate_service_request : {}".format(content) )
    sp = content['service_platform']
    ad = adapter.Adapter(sp) 
    LOG.debug("AuthManagerStoredVars: {}".format(ad.authmanager.__dict__))
    LOG.debug("UploaderStoredVars: {}".format(ad.uploader.__dict__)) 
    return ad.instantiateService(request)  
   
@app.route('/adapters/instantiate_service/tests', methods=['POST'])
def adapter_instatiate_service_tests():
    LOG.debug(request.is_json)
    content = request.get_json()
    sp = content['service_platform']
    ad = adapter.Adapter(sp) 
    LOG.debug(content) 
    return ad.instantiateServiceTest(request)     

@app.route('/adapters/instantiate_service/remotetests', methods=['POST'])
def adapter_instatiate_service_remote_tests():
    LOG.debug(request.is_json)
    content = request.get_json()
    sp = content['service_platform']
    ad = adapter.Adapter(sp) 
    LOG.debug(content) 
    return ad.instantiateServiceRemoteTest(request)  

@app.route('/adapters/download-upload-test', methods=['POST'])
def adapterDownloadUploadTest():
    LOG.debug(request.is_json)
    content = request.get_json()
    sp = content['service_platform']
    ad = adapter.Adapter(sp) 
    LOG.debug(content) 
    return ad.DownloadUploadTest(request)   

@app.route('/adapters/getOSMServiceId/tests', methods=['POST'])
def getOSMServiceIdTest():
    LOG.debug(request.is_json)
    content = request.get_json()
    LOG.debug(content) 
    sp = content['service_platform']
    ad = adapter.Adapter(sp) 
    #LOG.debug(content) 
    s_id = ad.getOSMServiceId(content['service_name'],content['service_vendor'],content['service_version'])
    LOG.debug(s_id)
    return  s_id

@app.route('/adapters/<service_platform>/requests/<id>', methods=['GET'])
def getSonataRequest(service_platform,id):   
    ad = adapter.Adapter(service_platform) 
    #return ad.getSonataRequest(id)       
    cosa =  ad.getSonataRequest(id)
    cosa_json = json.loads(cosa)       
    #return cosa_json['error']
    cosa_string = '\"error\": \"' + cosa_json['error'] + '\"'
    return cosa_string

@app.route('/service_platforms/<service_platform>/ip', methods=['GET'])
def get_sp_ip(service_platform):
    #LOG.debug(request.is_json)
    #content = request.get_json()
    #LOG.debug(content)
    ad = adapter.Adapter(service_platform)  
    #LOG.debug(ad.name)         
    return ad.getSPIp()    



from flask_cors import CORS
CORS(app)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
  return response

#MAIN FUNCTION OF THE SERVER

if __name__ == '__main__':
    #READ CONFIG
    conf_parser = argparse.ArgumentParser( description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, add_help=True )
    conf_parser.add_argument("-c", "--conf_file", help="Specify config file", metavar="FILE", default='config.cfg')
    args, remaining_argv = conf_parser.parse_known_args()
    config = ConfigParser()
    config.read(args.conf_file)
    createUsersObj = utils.Utils()
    createUsersObj.createTableUsers("db-config.cfg")
    createUsersObj.createTableServicePlatforms("db-config.cfg")    
    #RUN SERVER
    app.run(debug=True,host='0.0.0.0',port=5001)

