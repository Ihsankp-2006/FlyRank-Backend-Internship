import os

from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

security = HTTPBearer()

@app.get("/")
def root():
    return {
        "name": "FlyRank Auth API",
        "status": "running"
    }


@app.post("/auth/signup", status_code=201)
def signup(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        return {
            "id": response.user.id,
            "email": response.user.email
        }

    except Exception as e:
        print("SUPABASE SIGNUP ERROR:", e)
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.post("/auth/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JSONResponse(
            status_code=400,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )


@app.get("/public/info")
def public_info():
    return {
        "message": "This is a public endpoint"
    }


def require_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
        return response.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

   
@app.get("/protected/profile")
def protected_profile(user=Depends(require_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


@app.get("/protected/info")
def protected_info(user=Depends(require_user)):
    return {
        "message": "This is a protected endpoint",
        "user_id": user.id
    }


@app.post("/auth/logout", status_code=204)
def logout(user=Depends(require_user)):
    try:
        supabase.auth.sign_out()
        return
    except Exception:
        return
    