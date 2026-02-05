# appwrite_client.py
from dotenv import load_dotenv
import os
from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.database import Database  # <- fixed for Appwrite v14+

# ================= LOAD ENV =================
load_dotenv()

# ================= APPWRITE CORE =================
APPWRITE_ENDPOINT = os.getenv("https://nyc.cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("696f9104001dfedc5e1a")
API_KEY = os.getenv("APPWRITE_API_KEY")  # <- set this in .env or Render secret
DATABASE_ID = os.getenv("6970722d00269d80304f")

# ================= COLLECTION IDS =================
USERS_COLLECTION = os.getenv("users_collections")
WALLETS_COLLECTION = os.getenv("wallets")
BANK_DETAILS_COLLECTION = os.getenv("bank_details")
INVESTMENTS_COLLECTION = os.getenv("investments")
FUND_REQUESTS_COLLECTION = os.getenv("fund_requests")
WITHDRAWAL_REQUESTS_COLLECTION = os.getenv("withdraw_requests")

# ================= ADMIN =================
ADMIN_USER_ID = os.getenv("697e0cadc1dc567c1da9")

# ================= FASTAPI JWT SETTINGS (not Appwrite) =================
JWT_SECRET = os.getenv("JWT_SECRET_KEY")  # <- set this in .env or Render secret
JWT_ALGORITHM = os.getenv("HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))

# ================= CLIENT INIT =================
client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API Key (NOT JWT)

# ================= SERVICES =================
users = Users(client)
database = Database(client)  # <- singular, matches main.py