# importing packages
import os
# from dotenv import load_dotenv
# from pathlib import Path

# # set path to .env file
# basedir = Path(os.path.abspath(os.path.dirname(__file__))).parent

# # load the variables from the .env file in the environment strings
# load_dotenv(os.path.join(basedir, '.env'))

# define the object
class Config(object):
  """
  Config class that holds the database credentials as variables.
  """

  # load all the different database credentials into variables
  MYSQL_USER = os.environ['MYSQL_USER']
  MYSQL_PASS = os.environ['MYSQL_PASS']
  HOST = os.environ['HOST']
  PORT = int(os.environ['PORT'])
  DB = os.environ['DB']
  SSH_SERVER = os.environ['SSH_SERVER']
  SSH_PORT =  int(os.environ['SSH_PORT'])
  SSH_USER =  os.environ['SSH_USER']
  SSH_PASS =  os.environ['SSH_PASS']
  OPENAI = os.environ['open_ai_api']
