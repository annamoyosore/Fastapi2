from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from appwrite.client import Client
from appwrite.services import Users, Database  # Correct import for v14 SDK

# ================= APPWRITE CORE CONFIG =================

APPWRITE_ENDPOINT = os.getenv ("https://nyc.cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("PROJECT_ID")
API_KEY = os.getenv("API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

# ================= COLLECTION IDS =================

USERS_COLLECTION = os.getenv("users_collections")
WALLETS_COLLECTION = os.getenv ("wallets")
BANK_DETAILS_COLLECTION = os.getenv("bank_details")
INVESTMENTS_COLLECTION = os.getenv("investment")
FUND_REQUESTS_COLLECTION = os.getenv("fundrequest")
WITHDRAWAL_REQUESTS_COLLECTION = os.getenv("withdraw_request")

# ================= ADMIN =================

ADMIN_USER_ID = os.getenv("697e0cadc1dc567c1da9")

# ================= CLIENT INIT =================

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API key for backend operations

# ================= SERVICES =================

users = Users(client)
db = Database(client)  # Database service