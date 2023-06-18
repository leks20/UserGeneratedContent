from motor import motor_asyncio

from conf.config import mongo_settings
from db import mongo


async def connect_to_mongo():
    mongo.mongo_client = motor_asyncio.AsyncIOMotorClient(
        mongo_settings.connect_ulr, uuidRepresentation='standard'
    )
