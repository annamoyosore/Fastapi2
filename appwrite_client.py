from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.database import Database  # Use Database, not Databases

# ================= APPWRITE CORE CONFIG =================

APPWRITE_ENDPOINT = "https://nyc.cloud.appwrite.io/v1"  # Replace with your endpoint
PROJECT_ID = "YOUR_PROJECT_ID"  # Your Appwrite project ID
API_KEY = "YOUR_SERVER_API_KEY"  # Server-side API key, keep secret

DATABASE_ID = "YOUR_DATABASE_ID"  # Your main database ID

# ================= COLLECTION IDS =================

USERS_COLLECTION = "users_collections"
WALLETS_COLLECTION = "wallets"
BANK_DETAILS_COLLECTION = "bank_details"
INVESTMENTS_COLLECTION = "investment"
FUND_REQUESTS_COLLECTION = "fundrequest"
WITHDRAWAL_REQUESTS_COLLECTION = "withdraw_request"

# ================= ADMIN =================

ADMIN_USER_ID = "YOUR_ADMIN_USER_ID"  # Your admin user ID

# ================= CLIENT INIT =================

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(PROJECT_ID)
client.set_key(API_KEY)  # Server API key for backend operations

# ================= SERVICES =================

users = Users(client)
db = Database(client)  # <-- Fixed to proper Database service