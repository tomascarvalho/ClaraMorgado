from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib import parse
import psycopg2
import os

# If using AWS
if 'RDS_HOSTNAME' in os.environ:
    database = os.environ['RDS_DB_NAME']
    user = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    host = os.environ['RDS_HOSTNAME']
    port = os.environ['RDS_PORT']

# If using heroku
elif 'DATABASE_URL' in os.environ:
    parse.uses_netloc.append("postgres")
    url = parse.urlparse(os.environ["DATABASE_URL"])
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port

if 'RDS_HOSTNAME' in os.environ:
    database = os.environ['RDS_DB_NAME']
    user = os.environ['RDS_USERNAME']
    password = os.environ['RDS_PASSWORD']
    host = os.environ['RDS_HOSTNAME']
    port = os.environ['RDS_PORT']

if 'ADM_PW' in os.environ and 'ADM_EMAIL' in os.environ:
    ADM_PW = os.environ['ADM_PW']
    ADM_EMAIL = os.environ['ADM_EMAIL']

if 'AWS_SECRET_ACCESS_KEY' in os.environ and 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


if 'EMAIL_FROM' in os.environ and 'EMAIL_PASSWORD' in os.environ:
    EMAIL_FROM = os.environ['EMAIL_FROM']
    EMAIL_FROM = os.environ['EMAIL_PASSWORD']


if 'APP_SECRET_KEY' in os.environ:
    APP_SECRET_KEY = os.environ['APP_SECRET_KEY']

engine = create_engine('postgresql://'+user +':'+ password + '@'+ host +':'+ port +'/'+ database)


Session = sessionmaker(bind=engine)
session = Session()
