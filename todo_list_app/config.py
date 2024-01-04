import os
import secrets

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

module_dir = os.path.dirname(__file__)

dotenv_path = os.path.join(module_dir, '..', '.env')

load_dotenv(dotenv_path)

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
JWT_SECRET_KEY = secrets.token_urlsafe(32)


templates_dir = os.path.join(module_dir, 'templates')
env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
