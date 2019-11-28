# Copyright (c) 2019 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

from adapters.interface import Interface
from logger import TangoLogger
import models.database as database
import logging
import psycopg2

_LOG = TangoLogger.getLogger('platform:adapter', log_level=logging.DEBUG, log_json=True)
# _LOG = logging.getLogger('flask.app')


class AuthManager(Interface):
    connection = None
    
    def __init__(self, name):
        # connect to docker
        Interface.__init__(self)
        db_type = self.__getDBType()
        vim_account = self.__getVimAccount()
        db_username = self.__getDBUserName()
        db_project_name = self.__getDBProjectName()
        db_password = self.__getDBPassword()
        db_project = self.__getDBProject()
        db_host = self.__getDBHost()
        mon_url = self.__getMonitoringURLs()
        sp_name = name
        
    
    def updateToken(self,token):
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = self.connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            #_LOG.debug(sp_name)
            #_LOG.info(sp_name)
            get_type = "SELECT type FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            #_LOG.info(get_type)
            #_LOG.debug(get_type)            
            update_token = "UPDATE service_platforms SET service_token = \'" +token+ "\' WHERE name = \'" +sp_name+ "\'"            
            #_LOG.debug(update_token)
            __LOG.info(update_token)
            cursor.execute(update_token)
            connection.commit()
            return "token updated", 200    
        except (Exception, psycopg2.Error) as error :
            __LOG.debug(error)
            __LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    _LOG.info("PostgreSQL connection is closed")



    def __getDBType(self):
        _LOG.info("getdbtype starts")
        
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_type = "SELECT type FROM service_platforms WHERE name=\'" +sp_name+ "\'"            
            cursor.execute(get_type)
            type = cursor.fetchone().__str__() 
            _LOG.info("dbtype : "+type)
            return type, 200           
            
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
            if(connection!= None) : 
                connection.close()

    def __getVimAccount(self):
        _LOG.info("getdbtype starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_type = "SELECT vim_account FROM service_platforms WHERE name=\'" +sp_name+ "\'"            
            cursor.execute(get_type)
            vimaccount = cursor.fetchone().__str__()             
            return vimaccount, 200
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed")                     




    def __getDBUserName(self):
        _LOG.info("getdbusername starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_username = "SELECT username FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            _LOG.debug(get_username)
            cursor.execute(get_username)
            username = cursor.fetchone().__str__()
            _LOG.debug("username: {}".format(username))              
            return username, 200
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    _LOG.debug("PostgreSQL connection is closed")


    def __getDBProjectName(self):
        _LOG.info("getprojectname starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_project_name = "SELECT project_name FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            #_LOG.debug(get_project_name)
            cursor.execute(get_project_name)
            projectname = cursor.fetchone().__str__()
            _LOG.debug("projectname: {}".format(projectname)) 
            return projectname, 200
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed")                    


    def __getDBPassword(self):
        _LOG.info("get password starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_password= "SELECT password FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            _LOG.debug(get_password)
            cursor.execute(get_password)
            password = cursor.fetchone().__str__()
            #_LOG.debug("password: {}".format(password)) 
            return password, 200
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed")      


    def __getDBProject(self):
        _LOG.info("get project starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_password= "SELECT project_name FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            _LOG.debug(get_password)
            cursor.execute(get_password)
            project = cursor.fetchone().__str__()
            _LOG.debug("project: {}".format(project)) 
            return project, 200
        except (Exception, psycopg2.Error) as error :
            #_LOG.debug(error)
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed")                                    




    def __getDBHost(self):
        _LOG.info("get dbhost starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            query = "SELECT host FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            _LOG.debug(query)
            cursor.execute(get_host)
            host = cursor.fetchone().__str__()
            return host, 200    
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed") 


    def __getMonitoringURLs(self):
        _LOG.info("get monitoring urls starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #_LOG.debug( connection.get_dsn_parameters(),"\n")
            get_type = "SELECT monitoring_urls FROM service_platforms WHERE name=\'" +sp_name+ "\'"
            _LOG.debug(get_type)
            cursor.execute(get_type)
            mon_url = cursor.fetchone().__str__()
            return mon_url, 200 
        except (Exception, psycopg2.Error) as error :
            _LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #_LOG.debug("PostgreSQL connection is closed")                     

