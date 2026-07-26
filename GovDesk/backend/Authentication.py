
import bcrypt
from pydantic import BaseModel
import sqlite3
from fastapi import APIRouter,HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import os
import jwt
from datetime import datetime,timedelta,UTC
from dotenv import load_dotenv
from collections import defaultdict
load_dotenv()
login_attempts=defaultdict(list)
MAX_LOGIN_ATTEMPTS=5
LOGIN_WINDOW_MINUTES=15
JWT_SECRET_KEY=os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM=os.environ["JWT_ALGORITHM"]
JWT_EXPIRATION_MINUTES=int(os.environ["JWT_EXPIRATION_MINUTES"])
auth_router=APIRouter()
security=HTTPBearer()
def get_db():
    db=sqlite3.connect("userdata.db")
    try:
        yield db
    finally:
        db.close()
with sqlite3.connect("userdata.db") as setup_conn:
    setup_conn.execute("""
        CREATE TABLE IF NOT EXISTS userdata(
            id INTEGER PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
    """)
    columns=setup_conn.execute("PRAGMA table_info(userdata)").fetchall()
    current_columns=[col[1] for col in columns]
    if "role" not in current_columns:
        setup_conn.execute("ALTER TABLE userdata ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'civilian'")
class Credentials(BaseModel):
    username:str
    password:str
def is_rate_limited(username:str)->bool:
    window_start=datetime.now(UTC)-timedelta(minutes=LOGIN_WINDOW_MINUTES)
    login_attempts[username]=[t for t in login_attempts[username] if t>window_start]
    return len(login_attempts[username])>=MAX_LOGIN_ATTEMPTS
def create_token(username:str,role:str)->str:
    payload={
        "sub":username,
        "role":role,
        "exp":datetime.now(UTC)+timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }
    token=jwt.encode(payload,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)
    return token
@auth_router.post("/register/")
def create_user(personal_data:Credentials,db:sqlite3.Connection=Depends(get_db)):
    cur=db.cursor()
    salt=bcrypt.gensalt()
    hashed_password=bcrypt.hashpw(personal_data.password.encode(),salt).decode()
    try:
        cur.execute("INSERT INTO userdata(username,password) VALUES(?,?)",(personal_data.username,hashed_password))
        db.commit()
        return{"id":cur.lastrowid}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400,detail="username already exists")
@auth_router.post("/login/")
def user_login(login_data:Credentials,db:sqlite3.Connection=Depends(get_db)):
    if is_rate_limited(login_data.username):
        raise HTTPException(status_code=429,detail="Too many login attempts,try again later")
    cur=db.cursor()
    cur.execute("SELECT * FROM userdata WHERE username=?",(login_data.username,))
    user_row=cur.fetchone()
    if user_row is None:
        login_attempts[login_data.username].append(datetime.now(UTC))
        raise HTTPException(status_code=400,detail="invalid user")
    password_hash=user_row[2]
    current_role=user_row[3]
    password_bytes=login_data.password.encode("utf-8")
    if not bcrypt.checkpw(password_bytes,password_hash.encode("utf-8")):
        login_attempts[login_data.username].append(datetime.now(UTC))
        raise HTTPException(status_code=400,detail="invalid user")
    login_attempts.pop(login_data.username,None)
    token=create_token(login_data.username,current_role)
    return{"access_token":token,"token_type":"bearer"}
def get_current_user(credentials: HTTPAuthorizationCredentials=Depends(security)):
    token=credentials.credentials
    try:
        payload=jwt.decode(token,JWT_SECRET_KEY,[JWT_ALGORITHM],options={"verify_signature":True})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail="login again please")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="token is invalid")
    return payload
@auth_router.get("/whoami/")
def whoami(user=Depends(get_current_user)):
    return user

        


            



