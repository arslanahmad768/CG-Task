import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DB_URL = os.getenv("DATABASE_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)

database = client.Graphers


