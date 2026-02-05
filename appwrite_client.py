from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from appwrite.client import Client
from appwrite.services import Users, Database  # Correct import for v14 SDK

# ================= APPWRITE CORE CONFIG =================

APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://nyc.cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")
API_KEY = os.getenv("API_KEY", "YOUR_SERVER_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID", "YOUR_DATABASE_ID")

# ================= COLLECTION IDS =================

USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users_collections")
WALLETS_COLLECTION = os.getenv("WALLETS_COLLECTION", "wallets")
BANK_DETAILS_COLLECTION = os.getenv("BANK_DETAILS_COLLECTION", "bank_details")
INVESTMENTS_COLLECTION = os.getenv("INVESTMENTS_COLLECTION", "investment")
FUND_REQUESTS_COLLECTION = os.getenv("FUND_REQUESTS_COLLECTION", "fundrequest")
WITHDRAWAL_REQUESTS_COLLECTION = os.getenv("WITHDRAWAL_REQUESTS_COLLECTION", "withdraw_request")

# ================= ADMIN =================

ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "697e0cadc1dc567c1da9")

# ================= CLIENT INIT =================

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API key for backend operations

# ================= SERVICES =================

users = Users(client)
db = Database(client)  # Database service