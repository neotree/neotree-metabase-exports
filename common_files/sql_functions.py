
from common_files.config import config
from common_files.format_error import formatError
from sqlalchemy import event, create_engine
import logging
import sys

params = config()
connectionstring = 'postgresql+psycopg2://' + \
    params["user"] + ':' + params["password"] + '@' + \
    params["host"] + ':' + '5432' + '/' + params["database"]
engine = create_engine(connectionstring, executemany_mode='batch')

def inject_sql(sql_script, file_name):
        ids = []
        try:
          result =engine.connect().execution_options(isolation_level="AUTOCOMMIT").execute(sql_script)
          for row in result:
              ids.append(row['card_id'])
          result.close()
          return ids
        except Exception as e:
            logging.error('Something went wrong with the SQL file');
            logging.error(formatError(e))
            sys.exit()
        logging.info('... {0} has successfully run'.format(file_name))
def inject_void_sql(sql_script, file_name): 
        try:
            engine.connect().execution_options(isolation_level="AUTOCOMMIT").execute(sql_script) 
        except Exception as e:
            logging.error('Something went wrong with the SQL file');
            logging.error(formatError(e))
            sys.exit()
        logging.info('... {0} has successfully run'.format(file_name))
