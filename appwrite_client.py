from dotenv import load_dotenv
import os
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases

# ================= LOAD ENV =================
load_dotenv()

# ================= APPWRITE CORE =================
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")

# ================= COLLECTION IDS =================
USERS_COLLECTION = os.getenv("USERS_COLLECTION")
WALLETS_COLLECTION = os.getenv("WALLETS_COLLECTION")
BANK_DETAILS_COLLECTION = os.getenv("BANK_DETAILS_COLLECTION")
INVESTMENTS_COLLECTION = os.getenv("INVESTMENTS_COLLECTION")
FUND_REQUESTS_COLLECTION = os.getenv("FUND_REQUESTS_COLLECTION")
WITHDRAWAL_REQUESTS_COLLECTION = os.getenv("WITHDRAWAL_REQUESTS_COLLECTION")

# ================= ADMIN =================
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

# ================= CLIENT INIT =================
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API Key (NOT JWT)

# ================= SERVICES =================
users = Users(client)
databases = Databases(client)