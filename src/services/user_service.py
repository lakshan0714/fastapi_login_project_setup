from datetime import datetime,timezone,timedelta
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user import User,Session
from src.schemas.UserSchemas import UserCreate
from fastapi import Cookie, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import logging


class UserSerivice:
    def __init__(self, db: AsyncSession):
        self.db = db


    
    async def signup_user(self, data: UserCreate):
        """Registers a new user in the system."""
        
        logging.info(f"Attempting to create user with email: {data}")
        result = await self.db.execute(select(User).where(User.email == data.email))
        existing_user = result.scalar_one_or_none()
        logging.debug(f"Existing user found: {existing_user}")

        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        logging.debug("hashing password")
        # test_hash = pwd_context.hash("test123")
        # print(pwd_context.verify("test123", test_hash))
        
        hashed_pw = pwd_context.hash(data.password)
        logging.info(f"Password hashed for user: {data.email}")


        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=hashed_pw,
            role=data.role.value,
        )

        logging.info(f"role:{data.role.value}") 

        try:
            logging.debug("adding user to db")
            self.db.add(new_user)
            logging.info("successfully user added")
            
            await self.db.commit()
            await self.db.refresh(new_user)
            logging.info("user added")
            return {"message": "User created successfully", "user": new_user ,"status_code": 200}
        
        except SQLAlchemyError as e:
            await self.db.rollback()  # Important to rollback on error
            error_message = f"Database error: {str(e)}"
            # You can be more specific with different exception types
            return {"error": error_message, "status_code": 500}
        
        except Exception as e:
            await self.db.rollback()  # Rollback for any other unexpected errors
            error_message = f"Unexpected error: {str(e)}"
            return {"error": error_message, "status_code": 500}

        
    


    async def authenticate_user(self,email:str,password:str):
        """Authenticates a user by email and password.""" 
        result=await self.db.execute(select(User).where(User.email==email))
        user=result.scalar_one_or_none()
        #user =await self.db.query(User).filter(User.email==email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not pwd_context.verify(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return user
    
    
    

    async def create_session(self,user_email:str):
        """Creates a new session for the user."""

        session_id = str(uuid.uuid4())  # Generate a unique session ID  
        new_session = Session(
            user_mail=user_email,
            session_id=session_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        self.db.add(new_session)
        await self.db.commit()
        self.db.refresh(new_session)
        return new_session
    

    async def validate_session(self, session_id: str):
        print(session_id)
        result = await self.db.execute(select(Session).where(Session.session_id == session_id))
        session = result.scalar_one_or_none()
        if session:
            result2=await self.db.execute(select(User).where(User.email==session.user_mail))
            user=result2.scalar_one_or_none()
    
        
        if not session :
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired")
        
        return session,user
    


    

    async def logout_user(self, session_id: str):
        """Logs out a user by deleting their session."""
        
        try:
            
                # Find the session
                result = await self.db.execute(select(Session).where(Session.session_id == session_id))
                session = result.scalar_one_or_none()
                
                if not session:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                # Delete the session
                await self.db.delete(session)
                
                # Explicitly flush to ensure deletion is processed
                await self.db.commit()
                
                 # Transaction will automatically commit when exiting the context
                return {"msg": "User logged out successfully"}
        
        except Exception as e:
            # Log the error for debugging
            # logger.error(f"Error during logout: {str(e)}")
            raise HTTPException(status_code=500, detail="Logout failed")
            


    async def get_current_user(session_id: str = Cookie(None), db: AsyncSession=Depends(get_db)):
            if not session_id:
                raise HTTPException(status_code=401, detail="Missing session ID")

            user_service = UserSerivice(db)
            try:
                _, user = await user_service.validate_session(session_id)
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")
                return user
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to validate session")
            
