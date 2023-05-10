import os
from dotenv import load_dotenv


load_dotenv()

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
COMMUNITY_TOKEN = os.getenv('COMMUNITY_TOKEN')
USER_ID = os.getenv('USER_ID')
CONN_DB = os.getenv('CONN_DB')
