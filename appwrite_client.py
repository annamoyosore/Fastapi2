# appwrite_client.py
from dotenv import load_dotenv
import os
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases  # <- fixed for Appwrite v14+

# ================= LOAD ENV =================
load_dotenv()

# ================= APPWRITE CORE =================
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://nyc.cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "696f9104001dfedc5e1a")
API_KEY = os.getenv("APPWRITE_API_KEY")  # <- set this in .env or Render secret
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "6970722d00269d80304f")

# ================= COLLECTION IDS =================
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users_collections")
WALLETS_COLLECTION = os.getenv("WALLETS_COLLECTION", "wallets")
BANK_DETAILS_COLLECTION = os.getenv("BANK_DETAILS_COLLECTION", "bank_details")
INVESTMENTS_COLLECTION = os.getenv("INVESTMENTS_COLLECTION", "investments")
FUND_REQUESTS_COLLECTION = os.getenv("FUND_REQUESTS_COLLECTION", "fund_requests")
WITHDRAWAL_REQUESTS_COLLECTION = os.getenv("WITHDRAWAL_REQUESTS_COLLECTION", "withdraw_requests")

# ================= ADMIN =================
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID", "697e0cadc1dc567c1da9")

# ================= FASTAPI JWT SETTINGS (not Appwrite) =================
JWT_SECRET = os.getenv("JWT_SECRET_KEY")  # <- set this in .env or Render secret
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

# ================= CLIENT INIT =================
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API Key (NOT JWT)

# ================= SERVICES =================
users = Users(client)
database = Databases(client)  # <- note the plural 'Databases'