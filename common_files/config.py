from configparser import ConfigParser
#import libraries
import sys
import logging
import os
import stat
from pathlib import Path

# Create Log File If Not Exists
logfile = Path('/var/log/metabase_export.log')
logfile.touch(exist_ok=True)

# Configure Global Logger :: These settings will apply everywhere where thr logging library is called
logging.basicConfig(level=logging.INFO, filename=logfile, filemode="a+",
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# Set up logging to console
console = logging.StreamHandler()
# Set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
# Add the handler to the root logger
logging.getLogger('').addHandler(console)


if len(sys.argv) > 1:
    env = sys.argv[1]

    def config(filename='common_files/database.ini'):
        if env == "prod":
            section = 'postgresql_prod'
        elif env == "stage":
            section = 'postgresql_stage'
        elif env == "dev":
            section = 'postgresql_dev'

        else:
            logging.error("{0} is not a valid arguement: Valid arguements are (dev stage or prod)".format(env))
            sys.exit()

         # create a parser
        parser = ConfigParser()
        # read config file
        parser.read(filename)

        # get section, default to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
        # add environment to global params for use by other functions
            db['env'] = env
            for param in params:
                db[param[0]] = param[1]
        else:
            logging.error('Section {0} not found in the {1} file'.format(section, filename))
            sys.exit()
        
        return db
else:
    logging.error("Please include environment arguement (e.g. $ python metabase_export.py prod)")
    sys.exit()
