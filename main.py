from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from appwrite_client import (
    users,
    database,  # <- fixed: use 'database' instead of 'db'
    DATABASE_ID,
    ADMIN_USER_ID,
    WALLETS_COLLECTION,
    INVESTMENTS_COLLECTION,
    BANK_DETAILS_COLLECTION,
    FUND_REQUESTS_COLLECTION,
    WITHDRAWAL_REQUESTS_COLLECTION
)
import uuid, jwt, os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG =================
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 1440))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= SCHEMAS =================
class Login(BaseModel):
    email: str
    password: str

class Invest(BaseModel):
    plan: str
    amount: float

class FundRequest(BaseModel):
    amount: float

class WithdrawalRequest(BaseModel):
    amount: float

class BankDetails(BaseModel):
    bankName: str
    accountName: str
    accountNumber: str

# ================= JWT HELPERS =================
def create_jwt(user_id: str):
    payload = {
        "sub": user_id,
        "role": "admin" if user_id == ADMIN_USER_ID else "user",
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ")[1]

    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# ================= HEALTH =================
@app.get("/")
def root():
    return {"status": "alive"}

# ================= LOGIN =================
@app.post("/login")
def login(data: Login):
    try:
        session = users.create_email_password_session(
            email=data.email,
            password=data.password
        )

        user_id = session["userId"]

        wallets = database.list_documents(
            DATABASE_ID, WALLETS_COLLECTION,
            queries=[f"userId={user_id}"]
        )

        if wallets["total"] == 0:
            database.create_document(
                DATABASE_ID,
                WALLETS_COLLECTION,
                str(uuid.uuid4()),
                {
                    "userId": user_id,
                    "balance": 0,
                    "createdAt": datetime.utcnow().isoformat()
                }
            )

        return {"token": create_jwt(user_id)}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ================= WALLET =================
@app.get("/wallet")
def wallet(user=Depends(get_current_user)):
    wallet = database.list_documents(
        DATABASE_ID, WALLETS_COLLECTION,
        queries=[f"userId={user['sub']}"]
    )["documents"][0]

    return {"balance": wallet["balance"]}

# ================= INVEST =================
@app.post("/invest")
def invest(data: Invest, user=Depends(get_current_user)):
    wallet = database.list_documents(
        DATABASE_ID, WALLETS_COLLECTION,
        queries=[f"userId={user['sub']}"]
    )["documents"][0]

    if wallet["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    database.update_document(
        DATABASE_ID, WALLETS_COLLECTION,
        wallet["$id"],
        {"balance": wallet["balance"] - data.amount}
    )

    return database.create_document(
        DATABASE_ID,
        INVESTMENTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "plan": data.plan,
            "amount": data.amount,
            "status": "active",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

# ================= USER REQUESTS =================
@app.post("/request-funds")
def request_funds(data: FundRequest, user=Depends(get_current_user)):
    return database.create_document(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "amount": data.amount,
            "status": "pending",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

@app.post("/request-withdrawal")
def request_withdrawal(data: WithdrawalRequest, user=Depends(get_current_user)):
    return database.create_document(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "amount": data.amount,
            "status": "pending",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

# ================= ADMIN =================
@app.get("/admin/fund-requests")
def admin_funds(admin=Depends(require_admin)):
    return database.list_documents(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        queries=["status=pending"]
    )["documents"]

@app.get("/admin/withdrawals")
def admin_withdrawals(admin=Depends(require_admin)):
    return database.list_documents(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        queries=["status=pending"]
    )["documents"]