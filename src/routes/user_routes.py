from fastapi import HTTPException

from fastapi import APIRouter, Depends,Response,Cookie
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.schemas.UserSchemas import UserCreate,Userlogin
from src.services.user_service import UserSerivice
import logging

user_router = APIRouter()


@user_router.post("/signup")
async def signup_route(data: UserCreate, db: AsyncSession = Depends(get_db)):

    """
    Create a new user account.
    
    Args:
        data: User creation data
        user_service: Injected user service
        
    Returns:
        JSON response with user data or error
        
    Raises:
        HTTPException: If user creation fails
    """
       
    user_object=UserSerivice(db)
    try:
      response=await user_object.signup_user(data)
      if response.get("status_code") == 200:
          return response
      
      else:
          raise HTTPException(status_code=response.get("status_code", 500), detail=response.get("error", "An error occurred"))      

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)





@user_router.post("/login")
async def login_route(data: Userlogin,response:Response, db: AsyncSession = Depends(get_db)):
    user_object=UserSerivice(db)
    user = await user_object.authenticate_user(data.email, data.password)
   

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    try:
      #creating a session
      session =await user_object.create_session(data.email)
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    
    response.set_cookie(
        key="session_id",
        value=session.session_id,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="Lax",
        expires=session.expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )


    return {"message": "Login successful","data":user}




@user_router.get("/me")
async def get_me(session_id:str=Cookie(None),db=Depends(get_db)):
    user_object=UserSerivice(db)
    session,user=await user_object.validate_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {
        "data": user
    }




@user_router.post("/logout")
async def logout_route(response:Response,session_id: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if session_id:
        user_object = UserSerivice(db)
        await user_object.logout_user(session_id)
        response.delete_cookie("session_id")
        return {"message": "Logout successful"}
    
    else:
        raise HTTPException(status_code=400, detail="No session found")