from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib import parse
import psycopg2
import os

#Database config
database = 'dbname'
user = 'dbuser'
password = 'dbpassword'
host = 'localhost'
port = '5433'

#Credentials for admin account
ADM_EMAIL = 'admin@email.com'
ADM_PW = 'adminpassword'

#AWS keys with s3 bucket write permissions
AWS_ACCESS_KEY_ID = 'your_access_key'
AWS_SECRET_ACCESS_KEY = 'your_secret_key'

#Email credentials for the emailer
EMAIL_FROM = 'your@email.here'
EMAIL_PASSWORD = 'emailpasswordhere'

#The app secret key
APP_SECRET_KEY = 'your_secret_key'

engine = create_engine('postgresql://'+user +':'+ password + '@'+ host +':'+ port +'/'+ database)


Session = sessionmaker(bind=engine)
session = Session()
