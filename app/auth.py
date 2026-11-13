import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .db import User, get_async_session
from uuid import UUID

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto") # deprecated auto means it will automatically mark old hashes as deprecated when they are generated with an older scheme.

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str)->bool:
    return pwd_context.verify(password,hashed_password)

def create_access_token(user_id: UUID,) -> str:
    expire_date=datetime.utcnow() + timedelta(hours=24) # token will expire in 24 hours
    payload={
        "user_id":str(user_id),
        "exp":expire_date,
        "iat":datetime.utcnow()
    }
    token=jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)
    return token

def decode_access_token(token:str)-> UUID:
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM]) # payload will be a dictionary containing the user_id, exp, and iat
        return UUID(payload.get("user_id"))
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    
security=HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials= Depends(security),session: AsyncSession=Depends(get_async_session)):
    token=token.credentials
    try:
        user_id=decode_access_token(token)
        result= await session.execute(select(User).where(User.id==user_id))
        user=result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
