from motor.motor_asyncio import AsyncIOMotorClient
import certifi

MONGO_URL = "mongodb+srv://olivia:olivia@img-vid.tnzijmu.mongodb.net/ai_video_app?retryWrites=true&w=majority"

client = AsyncIOMotorClient(
    MONGO_URL,
    tlsCAFile=certifi.where()
)

db = client["ai_video_app"]

users = db["users"]
videos_collection = db["videos"]