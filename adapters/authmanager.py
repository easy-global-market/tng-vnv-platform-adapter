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

LOG = TangoLogger.getLogger("authmanager", log_level=logging.DEBUG, log_json=True)

LOG.setLevel(logging.DEBUG)
#LOG.info("Hello world.")

FILE = "db-config.cfg"

class AuthManager:

    def __init__(self, name):
        
        logging.getLogger().setLevel(logging.DEBUG)
        self.name = name
        LOG.info("AuthManagerConstructor")
        
        self.db_type = self.__getDBType()
        self.vim_account = self.__getVimAccount()
        self.db_username = self.__getDBUserName()
        self.db_project_name = self.__getDBProjectName()
        self.db_password = self.__getDBPassword()
        self.db_project = self.__getDBProject()
        self.db_host = self.__getDBHost()
        self.mon_url = self.__getMonitoringURLs()
    
    def __getDBType(self):
        LOG.info("getdbtype starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query = "SELECT type FROM service_platforms WHERE name=\'" +self.name+ "\'"            
            cursor.execute(query)
            type = cursor.fetchone()[0] 
            LOG.debug("dbtype: {}".format(type))
            return type           
            
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed") 

    def __getVimAccount(self):
        LOG.info("getdbtype starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query = "SELECT vim_account FROM service_platforms WHERE name=\'" +self.name+ "\'"            
            cursor.execute(query)
            vimaccount = cursor.fetchone()[0]   
            LOG.debug("vimaccount: {}".format(vimaccount))      
            return vimaccount
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed")                     




    def __getDBUserName(self):
        LOG.info("getdbusername starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query = "SELECT username FROM service_platforms WHERE name=\'" +self.name+ "\'"
            cursor.execute(query)
            username = cursor.fetchone()[0]
            LOG.debug("username: {}".format(username)) 
            return username
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    LOG.debug("PostgreSQL connection is closed")


    def __getDBProjectName(self):
        LOG.info("getprojectname starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query = "SELECT project_name FROM service_platforms WHERE name=\'" +self.name+ "\'"
            cursor.execute(query)
            project_name = cursor.fetchone()[0]
            LOG.debug("project_name: {}".format(project_name))
            return project_name
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed")                    


    def __getDBPassword(self):
        LOG.info("get password starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query= "SELECT password FROM service_platforms WHERE name=\'" +self.name+ "\'"
            LOG.debug(query)
            cursor.execute(query)
            password = cursor.fetchone()[0]
            return password
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed")      


    def __getDBProject(self):
        LOG.info("get project starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query= "SELECT project_name FROM service_platforms WHERE name=\'" +self.name+ "\'"
            cursor.execute(query)
            project_name = cursor.fetchone()[0]
            LOG.debug("project_name: {}".format(project_name))
            return project_name
        except (Exception, psycopg2.Error) as error :
            #LOG.debug(error)
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed")                                    




    def __getDBHost(self):
        LOG.info("get dbhost starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            #LOG.debug(self.name)
            query = "SELECT host FROM service_platforms WHERE name=\'" +self.name+ "\'"
            cursor.execute(query)
            host = cursor.fetchone()[0]
            LOG.debug("host: {}".format(host))
            return host    
        except (Exception, psycopg2.Error) as error :
            #LOG.debug(error)
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed") 


    def __getMonitoringURLs(self):
        LOG.info("get monitoring urls starts")
        try:
            db = database.Database(FILE)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)  
            cursor = connection.cursor()
            #LOG.debug( connection.get_dsn_parameters(),"\n")
            query = "SELECT monitoring_urls FROM service_platforms WHERE name=\'" +self.name+ "\'"
            cursor.execute(query)
            monitoring_urls = cursor.fetchone()[0]
            LOG.debug("monitoring_urls: {}".format(monitoring_urls))
            return monitoring_urls
        except (Exception, psycopg2.Error) as error :
            LOG.error(error)
            exception_message = str(error)
            return exception_message, 401
        finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    #LOG.debug("PostgreSQL connection is closed")       