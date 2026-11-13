from fastapi import Depends, FastAPI, HTTPException, File, UploadFile, Form
import os
import shutil
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .db import create_db_and_tables, get_async_session, Post, engine, User
from .schemas import PostCreate, PostRead, UserRegister, UserLogin, UserResponse, TokenResponse
from .auth import hash_password, verify_password, create_access_token, get_current_user
import logging
from uuid import UUID
from fastapi.staticfiles import StaticFiles
import shutil
import tempfile
from .image_utils import ik
# . means that this file is in the inside of this folder (the same loc as the app.py)

logging.basicConfig(
    level=logging.INFO
)  # normally log is set to warning, here we are changing it to info


@asynccontextmanager  # contextmanager boyuyub async olub, starting ve cleaning e imkan verir
async def lifespan(app: FastAPI):  # must include app even if you dont use it
    # create db (shutdown, cleaning part not included)
    try:
        await create_db_and_tables()
        logging.info("Database created successfully!")
    except Exception as e:
        logging.error(f"Database setup failed :( {e}")
        raise

    yield

    try:
        await engine.dispose()  # database connection is ended here
        logging.info("Cleanup complete")
    except Exception as e:
        logging.error(f"Cleanup failed {e}")


app = FastAPI(lifespan=lifespan)


@app.get("/")  # root endpoint
def root():
    return {"message": "Social media is running"}

@app.post("/auth/register",response_model=UserResponse)
async def register(user_data: UserRegister, session: AsyncSession = Depends(get_async_session)):
    
    result=await session.execute(select(User.email).where(User.email==user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400,detail="User already exists")
    
    new_user=User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@app.post("/auth/login",response_model=TokenResponse)
async def login(user_data: UserLogin,session: AsyncSession=Depends(get_async_session)):
    result=await session.execute(select(User).where(User.email==user_data.email))
    user=result.scalar_one_or_none()
    if not user or not verify_password(user_data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Invalid email or password")
    token=create_access_token(str(user.id))
    return TokenResponse(access_token=token,token_type="bearer")

@app.get("/users/me",response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/upload", response_model=PostRead)
async def upload_file(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    caption: str = Form(...),
    file: UploadFile = File(...),
):
    temp_file_path = None

    suffix = os.path.splitext(file.filename)[1]  # gets the extension of the file

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)  # copy operation

    try:
        with open(temp_file_path, "rb") as image_file:
            upload_result = ik.files.upload(
                file=image_file,
                file_name=file.filename,
                use_unique_file_name=True,
            )

        if upload_result:
            new_post = Post(
                user_id=current_user.id,
                caption=caption,
                url=upload_result.url,
                file_type=file.content_type,
                file_name=upload_result.name,
            )
            session.add(new_post)
            await session.commit()
            await session.refresh(new_post)  # use await for every database interaction
            return new_post
        else:
            raise HTTPException(status_code=500, detail="File upload failed")
    except Exception as e:
        logging.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.get("/posts", response_model=list[PostRead])
async def get_posts(session: AsyncSession = Depends(get_async_session),current_user: User = Depends(get_current_user)):
    result = await session.execute(select(Post))
    return result.scalars().all()


@app.get("/posts/{post_id}", response_model=PostRead)
async def get_post(post_id: UUID,current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.delete("/posts/{post_id}")
async def delete_post(post_id: UUID,current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        result=await session.execute(select(Post).where(Post.id==post_id))
        post=result.scalar_one_or_none()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if post.user_id!=current_user.id:
            raise HTTPException(status_code=403, detail="You are not authorized to delete this post")
        await session.delete(post)
        await session.commit()
        return {"success":True,"message": "Post deleted successfully"}
    except Exception as e:
        logging.error(f"Deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Post deletion failed: {str(e)}")
