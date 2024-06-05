import os

from dotenv import load_dotenv

load_dotenv()

JWT_PRIVATE_KEY = os.environ["JWT_PRIVATE_KEY"]
JWT_PUBLIC_KEY1 = os.environ["JWT_PUBLIC_KEY1"]
JWT_PUBLIC_KEY2 = os.environ["JWT_PUBLIC_KEY2"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
