"""MongoDB connection manager"""
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from config.settings import MONGODB_URI, DATABASE_NAME
import logging

logger = logging.getLogger(__name__)

# Global MongoDB client
_client = None
_db = None


def get_client():
    """Get MongoDB client instance"""
    global _client
    
    if not MONGODB_URI:
        raise ConfigurationError(
            "MONGODB_URI is not set. Please create a .env file with your MongoDB connection string.\n"
            "Example: MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/"
        )
    
    if _client is None:
        try:
            _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test the connection
            _client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except ServerSelectionTimeoutError as e:
            raise ConnectionError(
                f"Failed to connect to MongoDB. Please check:\n"
                f"1. Your MONGODB_URI in .env file is correct\n"
                f"2. Your MongoDB server is running and accessible\n"
                f"3. Your network connection is working\n"
                f"Original error: {str(e)}"
            ) from e
        except Exception as e:
            raise ConnectionError(
                f"Error connecting to MongoDB: {str(e)}\n"
                f"Please check your MONGODB_URI in .env file"
            ) from e
    
    return _client


def get_database():
    """Get database instance"""
    global _db
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
    return _db


def close_connection():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
        _client = None
