from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from appwrite_client import (
    users, db, DATABASE_ID, ADMIN_USER_ID, APPWRITE_ENDPOINT, PROJECT_ID, API_KEY,
    WALLETS_COLLECTION, INVESTMENTS_COLLECTION, BANK_DETAILS_COLLECTION,
    FUND_REQUESTS_COLLECTION, WITHDRAWAL_REQUESTS_COLLECTION
)
import uuid
import requests
from datetime import datetime

# ================= CONFIG =================
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
def verify_jwt(jwt_token: str):
    """Verify JWT with Appwrite API and return user info"""
    url = f"{APPWRITE_ENDPOINT}/account/jwt/verify"
    headers = {
        "X-Appwrite-Project": PROJECT_ID,
        "X-Appwrite-Key": API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={"jwt": jwt_token})
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid JWT")
    return response.json()  # returns user info including userId

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ")[1]
    return verify_jwt(token)

def require_admin(user=Depends(get_current_user)):
    if user["userId"] != ADMIN_USER_ID:
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

        # Init wallet
        wallets = db.list_documents(
            DATABASE_ID, WALLETS_COLLECTION,
            queries=[f"userId={user_id}"]
        )
        if wallets["total"] == 0:
            db.create_document(
                DATABASE_ID,
                WALLETS_COLLECTION,
                str(uuid.uuid4()),
                {
                    "userId": user_id,
                    "balance": 0,
                    "createdAt": datetime.utcnow().isoformat()
                }
            )

        # Get JWT directly from Appwrite
        jwt_response = users.create_jwt()
        return {"token": jwt_response["jwt"]}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ================= WALLET =================
@app.get("/wallet")
def wallet(user=Depends(get_current_user)):
    wallet = db.list_documents(
        DATABASE_ID,
        WALLETS_COLLECTION,
        queries=[f"userId={user['userId']}"]
    )["documents"][0]

    return {"balance": wallet["balance"]}

# ================= INVESTMENTS =================
@app.post("/invest")
def invest(data: Invest, user=Depends(get_current_user)):
    wallet = db.list_documents(
        DATABASE_ID,
        WALLETS_COLLECTION,
        queries=[f"userId={user['userId']}"]
    )["documents"][0]

    if wallet["balance"] < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    db.update_document(
        DATABASE_ID,
        WALLETS_COLLECTION,
        wallet["$id"],
        {"balance": wallet["balance"] - data.amount}
    )

    return db.create_document(
        DATABASE_ID,
        INVESTMENTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["userId"],
            "plan": data.plan,
            "amount": data.amount,
            "status": "active",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

@app.get("/investments")
def investments(user=Depends(get_current_user)):
    return db.list_documents(
        DATABASE_ID,
        INVESTMENTS_COLLECTION,
        queries=[f"userId={user['userId']}"]
    )["documents"]

# ================= BANK DETAILS =================
@app.post("/bank-details")
def save_bank(data: BankDetails, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID,
        BANK_DETAILS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["userId"],
            **data.dict(),
            "createdAt": datetime.utcnow().isoformat()
        }
    )

# ================= USER REQUESTS =================
@app.post("/request-funds")
def request_funds(data: FundRequest, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["userId"],
            "amount": data.amount,
            "status": "pending",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

@app.post("/request-withdrawal")
def request_withdrawal(data: WithdrawalRequest, user=Depends(get_current_user)):
    return db.create_document(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        str(uuid.uuid4()),
        {
            "userId": user["userId"],
            "amount": data.amount,
            "status": "pending",
            "createdAt": datetime.utcnow().isoformat()
        }
    )

# ================= ADMIN =================
@app.get("/admin/fund-requests")
def admin_funds(admin=Depends(require_admin)):
    return db.list_documents(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        queries=["status=pending"]
    )["documents"]

@app.get("/admin/withdrawals")
def admin_withdrawals(admin=Depends(require_admin)):
    return db.list_documents(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        queries=["status=pending"]
    )["documents"]

@app.post("/admin/approve-fund/{request_id}")
def approve_fund(request_id: str, admin=Depends(require_admin)):
    req = db.get_document(DATABASE_ID, FUND_REQUESTS_COLLECTION, request_id)

    if req["status"] != "pending":
        raise HTTPException(status_code=400, detail="Already processed")

    wallet = db.list_documents(
        DATABASE_ID, WALLETS_COLLECTION,
        queries=[f"userId={req['userId']}"]
    )["documents"][0]

    db.update_document(
        DATABASE_ID,
        WALLETS_COLLECTION,
        wallet["$id"],
        {"balance": wallet["balance"] + req["amount"]}
    )

    db.update_document(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        request_id,
        {"status": "approved", "approvedAt": datetime.utcnow().isoformat()}
    )

    return {"message": "Fund approved"}

@app.post("/admin/reject-fund/{request_id}")
def reject_fund(request_id: str, admin=Depends(require_admin)):
    db.update_document(
        DATABASE_ID,
        FUND_REQUESTS_COLLECTION,
        request_id,
        {"status": "rejected", "approvedAt": datetime.utcnow().isoformat()}
    )
    return {"message": "Fund rejected"}

@app.post("/admin/approve-withdrawal/{request_id}")
def approve_withdrawal(request_id: str, admin=Depends(require_admin)):
    req = db.get_document(DATABASE_ID, WITHDRAWAL_REQUESTS_COLLECTION, request_id)

    wallet = db.list_documents(
        DATABASE_ID,
        WALLETS_COLLECTION,
        queries=[f"userId={req['userId']}"]
    )["documents"][0]

    if wallet["balance"] < req["amount"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    db.update_document(
        DATABASE_ID,
        WALLETS_COLLECTION,
        wallet["$id"],
        {"balance": wallet["balance"] - req["amount"]}
    )

    db.update_document(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        request_id,
        {"status": "approved", "approvedAt": datetime.utcnow().isoformat()}
    )

    return {"message": "Withdrawal approved"}

@app.post("/admin/reject-withdrawal/{request_id}")
def reject_withdrawal(request_id: str, admin=Depends(require_admin)):
    db.update_document(
        DATABASE_ID,
        WITHDRAWAL_REQUESTS_COLLECTION,
        request_id,
        {"status": "rejected", "approvedAt": datetime.utcnow().isoformat()}
    )
    return {"message": "Withdrawal rejected"}