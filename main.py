from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from appwrite_client import users, db, DATABASE_ID, ADMIN_USER_ID
import uuid, jwt
from datetime import datetime, timedelta

# ================= CONFIG =================
JWT_SECRET = "CHANGE_THIS_SECRET"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24

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
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
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

        # Init wallet if missing
        wallets = db.list_documents(
            DATABASE_ID, "wallets",
            queries=[f"userId={user_id}"]
        )
        if wallets["total"] == 0:
            db.create_document(
                DATABASE_ID, "wallets", str(uuid.uuid4()),
                {"userId": user_id, "balance": 0}
            )

        token = create_jwt(user_id)
        return {"token": token}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ================= WALLET =================
@app.get("/wallet")
def wallet(user=Depends(get_current_user)):
    wallet = db.list_documents(
        DATABASE_ID, "wallets",
        queries=[f"userId={user['sub']}"]
    )["documents"][0]

    return {"balance": wallet["balance"]}

# ================= INVEST =================
@app.post("/invest")
def invest(data: Invest, user=Depends(get_current_user)):
    wallet = db.list_documents(
        DATABASE_ID, "wallets",
        queries=[f"userId={user['sub']}"]
    )["documents"][0]

    if wallet["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    db.update_document(
        DATABASE_ID, "wallets", wallet["$id"],
        {"balance": wallet["balance"] - data.amount}
    )

    return db.create_document(
        DATABASE_ID, "investments", str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "plan": data.plan,
            "amount": data.amount,
            "status": "active",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

@app.get("/investments")
def investments(user=Depends(get_current_user)):
    return db.list_documents(
        DATABASE_ID, "investments",
        queries=[f"userId={user['sub']}"]
    )["documents"]

# ================= BANK =================
@app.post("/bank-details")
def save_bank(data: BankDetails, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID, "bank_details", str(uuid.uuid4()),
        {
            "userId": user["sub"],
            **data.dict(),
            "createdAt": datetime.utcnow().isoformat()
        }
    )

# ================= REQUESTS =================
@app.post("/request-funds")
def request_funds(data: FundRequest, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID, "fund_requests", str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "amount": data.amount,
            "status": "pending"
        }
    )

@app.post("/request-withdrawal")
def request_withdrawal(data: WithdrawalRequest, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID, "withdrawal_requests", str(uuid.uuid4()),
        {
            "userId": user["sub"],
            "amount": data.amount,
            "status": "pending"
        }
    )

# ================= ADMIN =================
@app.get("/admin/fund-requests")
def admin_funds(admin=Depends(require_admin)):
    return db.list_documents(
        DATABASE_ID, "fund_requests",
        queries=["status=pending"]
    )["documents"]

@app.get("/admin/withdrawals")
def admin_withdrawals(admin=Depends(require_admin)):
    return db.list_documents(
        DATABASE_ID, "withdrawal_requests",
        queries=["status=pending"]
    )["documents"]