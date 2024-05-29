import motor.motor_asyncio
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

MONGO_DB_URL = os.getenv("DATABASE_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URL)

database = client.Graphers

async def test_connection():
    try:
        collections = await database.list_collection_names()
        print("Connected to MongoDB!")
        print("Collections in the database:", collections)
    except Exception as e:
        print("Failed to connect to MongoDB", e)

