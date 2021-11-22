import asyncio
from common_files.config import config
from common_files.format_error import formatError
from common_files.hospital_config import hospital_conf
from pyppeteer import launch
import logging
import sys
import os
import fnmatch
import shutil
import datetime
import jwt
import re
import json
from common_files.sql_functions import inject_sql,inject_void_sql
from queries.get_public_questions import get_public_questions

async def main():
    cwd = os.getcwd()
    params = config()
    hospitals = hospital_conf()
    secretKey = None
    export_dir = '/home/ubuntu/metabase_exports/'
    ids = []
    
    if hospitals:
        for hospital in hospitals:
            # Get Question Ids For Each Section as defined in the hospitals.ini file
            hospital_configuration = hospitals[hospital]
            demographics_ids = []
            hiv_status_ids = []
            outcomes_ids = []
            outcomes_268kg_ids = []
            temperatures_ids = []
            maternal_ids = []

            if 'demographics' in hospital_configuration:
                demographics_ids=  str(hospital_configuration['demographics']).split(",")
            if 'hiv_status' in hospital_configuration:
               hiv_status_ids = str(hospital_configuration['hiv_status']).split(",")
            if 'outcomes' in hospital_configuration:
                outcomes_ids= str(hospital_configuration['outcomes']).split(",")
            if 'outcomes_268' in hospital_configuration:
                outcomes_268kg_ids = str(hospital_configuration['outcomes_268']).split(",") 
            if 'temperatures' in hospital_configuration:
                temperatures_ids = str(hospital_configuration['temperatures']).split(",") 
            if 'maternals' in hospital_configuration:
                maternal_ids = str(hospital_configuration['maternals']).split(",") 

            demographics = []
            hiv_status = []
            outcomes =[]
            outcomes_268kg =[]
            temperatures = []
            maternals = []
            exports = {}

            metabase_url = None
            if 'export_dir' in hospital_configuration:
                export_dir = hospital_configuration['export_dir']
                if os.path.exists(export_dir):
                    for rootDir, subdirs, filenames in os.walk(export_dir):
                        for filename in fnmatch.filter(filenames, '*.png'):
                            try:
                                os.remove(os.path.join(rootDir, filename))
                            except:
                                pass;
                else:
                     os.mkdir(export_dir);
            else:
                if os.path.exists(export_dir):
                    pass;
                else:    
                    os.mkdir(export_dir);
               
            if 'metabase_secret' in params:
                secretKey = params['metabase_secret']
            if 'metabase_url' in params:
                metabase_url = params['metabase_url']
            #Enable Link Embedding So That The Script Can Successfully Export
            try:
                file_name = (cwd + "/queries/activate_embedding.sql")
                sql_file = open(file_name, "r")
                sql_script = sql_file.read()
                sql_file.close()
                inject_void_sql(sql_script, "activate_embedding")
            except Exception as e:
                logging.info('Something Wicked Happened During Activating Embedding')
                logging.error(formatError(e))
                sys.exit(1)
             #Fetch All Questions From The Database
            try:
                file_name = (cwd + "/queries/get_public_questions.sql")
                # Convert the dashboard Ids from String to int and pass them as a tuple
                #Dashboard Ids For Dashboards Where All Questions Are Compulsory
                dashboard_ids = tuple(map(int, str(hospital_configuration['dashboard_ids']).split(",")));
                # Question Ids To Facilitate For Or Query where not all questions are compulsory in a dashboard
                combine_question_ids =tuple(map(int,(demographics_ids + hiv_status_ids + outcomes_ids 
                                       + outcomes_268kg_ids+temperatures_ids+maternal_ids)))
                # Special Resolution IDs require full screen rendering
                special_resolution_ids = tuple()
                if 'special_resolution' in hospital_configuration:
                    special_resolution_ids = tuple(map(int,str(hospital_configuration['special_resolution']).split(",")))


            
                
                sql_script = get_public_questions(dashboard_ids,combine_question_ids);
                ids = inject_sql(sql_script, "getting_dashboard_cards")
            except Exception as e:
                logging.info('Something Wicked Happened During Activating Embedding')
                logging.error(formatError(e))
                sys.exit(1)
                #Loop through IDS, then Authenticate Each Question and Export It To Image
            screen_number =1
            for i ,id in enumerate(ids):
                token ={}
        
                payload = {
                "resource": { "question": id },
                "params": {},
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
                }
                token = jwt.encode(payload,secretKey)
                token = str(token)
                token = re.sub(r'^.*?\'', '', token)
                token = token.replace('\'','')
       
                try:
                    if export_dir is not None:
                        browser = await launch({'dumpio':True,'args': ['--no-sandbox', '--disable-setuid-sandbox','--headless','--disable-gpu','--disable-software-rasterizer','--disable-dev-shm-usage']})
                        page = await browser.newPage()
                        url = '{0}embed/question/{1}#bordered=true&titled=true'.format(metabase_url,token)
                        # Set a bigger Page View Port if the page is too big
                        if id in special_resolution_ids:
                            await page.setViewport({'width': 1920, 'height': 1080})
                        await page.goto(url,timeout=0,fullPage=True,waitUntil='networkidle0')
                        await page.screenshot({'path': '{0}image_{1}.png'.format(export_dir,id)})
                                                                
                        if str(id) in demographics_ids:
                            demographics.append('image_{0}.png'.format(id))
                        elif str(id) in hiv_status_ids:
                            hiv_status.append('image_{0}.png'.format(id))
                        elif str(id) in outcomes_268kg_ids:
                            outcomes_268kg.append('image_{0}.png'.format(id))
                        elif str(id) in outcomes_ids:
                            outcomes.append('image_{0}.png'.format(id))
                        elif str(id) in temperatures_ids:
                            temperatures.append('image_{0}.png'.format(id))

                        elif str(id) in maternal_ids:
                            maternals.append('image_{0}.png'.format(id))

                        else:
                            exports['screen_{0}'.format(screen_number)] =['image_{0}.png'.format(id)]
                            screen_number = screen_number+1

                        #await page.screenshot({'path': '{0}image_{1}.png'.format(export_dir,i)})
                        await browser.close()
                    else:
                        logging.info('Please specify directory to put your exports your database.ini file i.e export_dir')
                        sys.exit(1)
            
                except Exception as e:
                    logging.info('Something Wicked Happened During Images Exportation.')
                    logging.exception(e)
                    sys.exit(1)
                #Disable Link Embedding As A Security Measure
                try:
            
                    #Get image_paths Acoording to sorted IDs List
                    if demographics_ids and demographics:
                        exports['demographics'] = sorted(demographics, key=lambda x: list(map(int,demographics_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    if hiv_status_ids and hiv_status:
                        exports['hiv_status'] =  sorted(hiv_status, key=lambda x: list(map(int,hiv_status_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    if outcomes_ids and outcomes:
                        exports['outcomes'] =  sorted(outcomes, key=lambda x: list(map(int,outcomes_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    if outcomes_268kg_ids and outcomes_268kg:
                        exports['outcomes_268kg'] =sorted(outcomes_268kg, key=lambda x: list(map(int,outcomes_268kg_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    if temperatures_ids and temperatures:
                        exports['temperatures'] =sorted(temperatures, key=lambda x: list(map(int,temperatures_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    if maternal_ids and maternals:
                        exports['maternals'] =sorted(maternals, key=lambda x: list(map(int,maternal_ids)).index(int(''.join(d for d in x if d.isdigit()))))
                    #Write The Json To The File
                    try:
                        json_file = json.dumps(exports)
                        file = open("{0}metabase_exports.json".format(export_dir),"w")
                        file.write(json_file)
                        file.close()
                    except Exception as e:
                        logging.error(formatError(e))
                        sys.exit(1)
                except Exception as e:
                    logging.error(formatError(e))
                    sys.exit(1)
        try:
            file_name = (cwd + "/queries/deactivate_embedding.sql")
            sql_file = open(file_name, "r")
            sql_script = sql_file.read()
            sql_file.close()
            inject_void_sql(sql_script, "deactivate_embedding")
        except Exception as e:
            logging.info('Something Wicked Happened During Deactivating Embedding')
            logging.error(formatError(e))
            sys.exit(1)
        logging.info('Images Exported Successfully!!')
  
            # Writting To The Json File
        
        

asyncio.get_event_loop().run_until_complete(main());