from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()
DB_NAME = "CVcraft"

# Construct MongoDB URI using environment variables
MONGO_URI = "mongodb+srv://Rohan:Rohan123@learningcluster.nzkdrcs.mongodb.net/?retryWrites=true&w=majority&appName=LearningCluster"

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_collection = db["users"]
jobs_collection = db["jobs"]
templates_collection = db["templates"]
history_collection = db["history"]
