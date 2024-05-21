# from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import Union

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    email: Union[str, None] = None

class User(BaseModel):
    fullname: Union[str, None] = None
    email: EmailStr = Field(...)
    city: str = Field(..., min_length=1, max_length=50)
    
        
class UserInDB(User):
    password: str
    
    class Config:
        json_schema_extra  = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@x.edu.ng",
                "password": "strongpassword123",
                "city": "New York",
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}