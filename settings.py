import os
from os.path import dirname, join

from dotenv import load_dotenv

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
VOX_URL = os.environ.get("VOX_URL")
VOX_PORT = os.environ.get("VOX_PORT")
OPENAI_KEY = os.environ.get("OPENAI_KEY")
