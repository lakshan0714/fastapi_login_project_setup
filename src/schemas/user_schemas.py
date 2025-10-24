from pydantic import BaseModel, EmailStr
from sqlalchemy import Enum
import enum


class UserRole(enum.Enum):
    admin = "admin"
    superadmin ="superadmin"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole  # Must be one of 'creater', 'merchandiser', 'user'



class Userlogin(BaseModel):
    email: EmailStr
    password: str
   
