from crontab import CronTab
from common_files.config import config
import logging
from common_files.format_error import formatError
import sys
params = config()
#The execution environment to be used as set in the parameters
mode = params['env']
interval = 12
#The home directory of the data_pipeline.py file as set in the database.ini file
cronDir = None
if 'cron_dir' in params:
    cronDir = params['cron_dir']
#The number of hours before next execution of the next job as set in the database.ini file
if 'cron_interval'in params:
    interval = int(params['cron_interval'])

try:
# Set The User To Run The Cron Job
    cron = CronTab(user=True)
# Set The Command To Run The Data Pipeline script and activate the virtual environment
    if cronDir is not None:
        job = cron.new(command='cd {0} && env/bin/python  metabase_export.py {1}'.format(cronDir,mode))
    else:
        logging.info('Please specify directory to find your script in your database.ini file')
        sys.exit()
# Set The Time For The Cron Job
# Use job.minute for quick testing
    #job.minute.every(interval)
    job.every(interval).hours()
# Write the Job To CronTab
    cron.write( user=True )
    logging.info('Cron Job Set To Run On Every {0} hour Intervals'.format(interval))
    logging.info('After Execution Please Check in /var/log/metabase_export.log For Logs')
    
except Exception as e:
    logging.error("!!Cron Job Failed To Start Due To Errors: ")
    logging.error(formatError(e))
    sys.exit(1)

