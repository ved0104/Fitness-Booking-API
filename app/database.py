from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    try:
        mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb.database = mongodb.client[settings.DATABASE_NAME]
        
        await mongodb.client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
        
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


async def create_indexes():
    db = mongodb.database
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    
    # Fitness classes collection indexes
    await db.fitness_classes.create_index("dateTime")
    
    # Bookings collection indexes
    await db.bookings.create_index("class_id")
    await db.bookings.create_index("user_id")
    await db.bookings.create_index([("class_id", 1), ("user_id", 1)], unique=True)
    
    logger.info("Database indexes created successfully")


def get_database():
    return mongodb.database
