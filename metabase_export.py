import asyncio
from common_files.config import config
from common_files.format_error import formatError
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
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

async def main():
    cwd = os.getcwd()
    params = config()
    secretKey = None
    export_dir = '/home/ubuntu/metabase_exports/'
    ids = []
    demographics_ids = [178,98,99,134,100,101,106]
    hiv_status_ids =[111,112,113,114,116]
    outcomes_ids = [121,122,209]
    outcomes_268kg_ids =[123,124]
    demographics = []
    hiv_status = []
    outcomes =[]
    outcomes_268kg =[]
    exports = {}

    metabase_url = None
    if 'export_dir' in params:
        export_dir = params['export_dir']
        if os.path.exists(export_dir):
           for rootDir, subdirs, filenames in os.walk(export_dir):
               for filename in fnmatch.filter(filenames, '*.png'):
                    try:
                        os.remove(os.path.join(rootDir, filename))
                    except:
                        pass;
    else:
        if os.path.exists(export_dir):
            print()
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
        sql_file = open(file_name, "r")
        sql_script = sql_file.read()
        sql_file.close()
        ids = inject_sql(sql_script, "activate_embedding")
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
                browser = await launch({'dumpio':True ,'args': ['--no-sandbox', '--disable-setuid-sandbox','--headless','--disable-gpu','--disable-software-rasterizer','--disable-dev-shm-usage']})
                page = await browser.newPage()
                url = '{0}/embed/question/{1}#bordered=true&titled=true'.format(metabase_url,token)
                await page.goto(url,timeout=0,fullPage=True,waitUntil='networkidle0')
                await page.screenshot({'path': '{0}image_{1}.png'.format(export_dir,id)})
                
                if id in demographics_ids:
                    demographics.append('image_{0}.png'.format(id))
                elif id in hiv_status_ids:
                    hiv_status.append('image_{0}.png'.format(id))
                elif id in outcomes_268kg_ids:
                    outcomes_268kg.append('image_{0}.png'.format(id))
                elif id in outcomes_ids:
                    outcomes.append('image_{0}.png'.format(id))
                else:
                    exports['screen_{0}'.format(screen_number)] =['image_{0}.png'.format(id)]
                    screen_number = screen_number+1

                #await page.screenshot({'path': '{0}image_{1}.png'.format(export_dir,i)})
                await browser.close()
            else:
                logging.info('Please specify directory to put your exports your database.ini file i.e export_dir')
                logging.error(formatError(e))
                sys.exit(1)
    
        except Exception as e:
            logging.info('Something Wicked Happened During Images Exportation.')
            logging.error(e)
            sys.exit(1)
    #Disable Link Embedding As A Security Measure
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
    try:
       
        #Get image_paths Acoording to sorted IDs List
        exports['demographics'] = sorted(demographics, key=lambda x: demographics_ids.index(int(''.join(d for d in x if d.isdigit()))))
        exports['hiv_status'] =  sorted(hiv_status, key=lambda x: hiv_status_ids.index(int(''.join(d for d in x if d.isdigit()))))
        exports['outcomes'] =  sorted(outcomes, key=lambda x: outcomes_ids.index(int(''.join(d for d in x if d.isdigit()))))
        exports['outcomes_268kg'] =sorted(outcomes_268kg, key=lambda x: outcomes_268kg_ids.index(int(''.join(d for d in x if d.isdigit()))))

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
        

asyncio.get_event_loop().run_until_complete(main());