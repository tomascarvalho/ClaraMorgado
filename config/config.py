from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import os
import urllib.parse



if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }

elif 'DATABASE_URL' in os.environ:
    urllib.parse.uses_netloc.append("postgres")
    url = urllib.parse.urlparse(os.environ["DATABASE_URL"])
    DATABASES = {
        'default': {
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port,
        }
    }


if 'ADM_PW' in os.environ and 'ADM_EMAIL' in os.environ:
    ADM_PW = os.environ['ADM_PW']
    ADM_EMAIL = os.environ['ADM_EMAIL']

if 'AWS_SECRET_ACCESS_KEY' in os.environ and 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']


if 'EMAIL_FROM' in os.environ and 'EMAIL_PASSWORD' in os.environ and 'EMAIL_TO' in os.environ:
    EMAIL_FROM = os.environ['EMAIL_FROM']
    EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']
    EMAIL_TO = os.environ['EMAIL_TO']


if 'APP_SECRET_KEY' in os.environ:
    APP_SECRET_KEY = os.environ['APP_SECRET_KEY']

engine = create_engine('postgresql://'+DATABASES['default'].get('USER')+':'+ DATABASES['default'].get('PASSWORD') + '@'+ str(DATABASES['default'].get('HOST'))+':'+ str(DATABASES['default'].get('PORT')) +'/'+ DATABASES['default'].get('NAME'))


Session = sessionmaker(bind=engine)
session = Session()
