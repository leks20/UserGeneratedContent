from motor import motor_asyncio

from conf.config import mongo_settings

mongo_client: motor_asyncio.AsyncIOMotorClient | None = None


async def get_mongo() -> motor_asyncio.AsyncIOMotorClient:
    return mongo_client[mongo_settings.db_name]
