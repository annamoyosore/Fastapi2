from fastapi import FastAPI, Depends, HTTPException  # ✅ Import Depends and HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from appwrite_client import users, db, DATABASE_ID, ADMIN_USER_ID
import uuid
from datetime import datetime

app = FastAPI()  # ✅ Only one app instance

# ================= APP ALIVE CHECK =================
@app.get("/")
def root():
    return {"message": "Hello! App is alive ✅"}

@app.get("/alive")
def alive():
    return {"status": "App is live ✅"}

# ---------------- SCHEMAS ----------------
class Register(BaseModel):
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class Invest(BaseModel):
    userId: str
    plan: str
    amount: float

class FundRequest(BaseModel):
    userId: str
    amount: float

class WithdrawalRequest(BaseModel):
    userId: str
    amount: float

class BankDetails(BaseModel):
    userId: str
    bankName: str
    accountName: str
    accountNumber: str

# ---------------- INVESTMENT PLANS ----------------
INVESTMENT_PLANS = {
    "Crypto": {"roi": 12, "duration": 30},
    "Real Estate": {"roi": 8, "duration": 60},
    "Forex": {"roi": 10, "duration": 30},
    "Agriculture": {"roi": 7, "duration": 45},
    "Technology": {"roi": 15, "duration": 30},
    "Gold": {"roi": 6, "duration": 60},
}

# ---------------- ADMIN VERIFY ----------------
def verify_admin(userId: str):
    if userId != ADMIN_USER_ID:
        raise HTTPException(status_code=403, detail="Access forbidden: Admin only")
    return True

# ---------------- USER AUTH ----------------
@app.post("/register")
def register(data: Register):
    try:
        user = users.create(
            user_id=str(uuid.uuid4()),
            email=data.email,
            password=data.password
        )
        db.create_document(
            DATABASE_ID,
            "users",
            str(uuid.uuid4()),
            {
                "userId": user["$id"],
                "email": data.email,
                "balance": 0,
                "createdAt": datetime.utcnow().isoformat()
            }
        )
        return {"message": "User registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(data: Login):
    try:
        session = users.create_email_password_session(
            email=data.email,
            password=data.password
        )
        user_id = session["userId"]

        wallets = db.list_documents(
            DATABASE_ID,
            "wallets",
            queries=[f"userId={user_id}"]
        )

        if wallets["total"] == 0:
            db.create_document(
                DATABASE_ID,
                "wallets",
                str(uuid.uuid4()),
                {
                    "userId": user_id,
                    "balance": 0,
                    "createdAt": datetime.utcnow().isoformat()
                }
            )
        return {"userId": user_id}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ================= REST OF YOUR ROUTES =================
# Bank details, investment, fund requests, withdrawals, admin endpoints
# ... (keep all your existing code here)