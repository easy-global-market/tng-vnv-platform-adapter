#!/usr/bin/python

import psycopg2
import requests

from flask import Flask, request, jsonify, render_template
import os, sys, logging, json, argparse 
from configparser import ConfigParser
import models.database as database


class Utils:

    def createTableUsers(self,file):
        connection = None
        try:
            db = database.Database(file)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database)            

#            connection = psycopg2.connect(user = "sonatatest",
#                                        password = "sonata",
#                                        host = "172.18.0.2",
#                                        port = "5432",
#                                        database = "gatekeeper")
            cursor = connection.cursor()
            print ( connection.get_dsn_parameters(),"\n")
            #create table PM-USERS        
            create_users = ("""
                    CREATE TABLE pm_users (
                        username varchar(40) PRIMARY KEY, 
                        password varchar(40), 
                        service_platform varchar(40)                    
                        )
                        """)                       
            cursor.execute(create_users)
            connection.commit()
            create_text = "Users table created"
            return jsonify(create_text), 200

        except (Exception, psycopg2.Error) as error :
            #print ("Error while connecting to PostgreSQL", error)
            print (error)
            exception_message = str(error)
            return exception_message, 401
        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")

    def createTableServicePlatforms(self,file):
        connection = None
        try:
            db = database.Database(file)
            connection = psycopg2.connect(user = db.user,
                                        password = db.password,
                                        host = db.host,
                                        port = db.port,
                                        database = db.database) 
            cursor = connection.cursor()
            print ( connection.get_dsn_parameters(),"\n")
            #create table Service Platforms
            create_sps = ("""
                    CREATE TABLE service_platforms (
                        name varchar(40) PRIMARY KEY, 
                        host varchar(255), 
                        type varchar(40),
                        username varchar(255),
                        password varchar(255),
                        project_name varchar(255),
                        vim_account varchar(255),
                        service_token varchar(256),
                        monitoring_urls varchar(256)
                        )
                        """)               
            cursor.execute(create_sps)
            connection.commit()
            create_text = "Service Platform table created"
            return jsonify(create_text), 200

        except (Exception, psycopg2.Error) as error :
            print (error)
            exception_message = str(error)
            return exception_message, 401
        finally:
            #closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")                

