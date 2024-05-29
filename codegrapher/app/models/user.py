from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

class Token(BaseModel):
    """
    Token model to represent the access token and its type.

    Attributes:
        access_token (str): The JWT token string.
        token_type (str): The type of the token (e.g., "Bearer").
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    TokenData model to represent the token payload data.

    Attributes:
        email (EmailStr): The email address associated with the token.
    """
    email: EmailStr = Field(...)

class User(BaseModel):
    """
    User model to represent a user's information.

    Attributes:
        fullname (Union[str, None]): The full name of the user (optional).
        email (EmailStr): The email address of the user.
        city (str): The city where the user resides.
    """
    fullname: Union[str, None] = None
    email: EmailStr = Field(...)
    city: str = Field(..., min_length=1, max_length=50)
    disabled: Union[bool, None] = Field(default=False)

class UserInDB(User):
    """
    UserInDB model extends the User model to include a password attribute.

    Attributes:
        password (str): The user's password.

    Config:
        json_schema_extra (dict): Example of a user instance.
    """
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@x.edu.ng",
                "password": "strongpassword123",
                "city": "New York",
            }
        }

class UserLoginSchema(BaseModel):
    """
    UserLoginSchema model to represent the login data.

    Attributes:
        email (EmailStr): The email address of the user.
        password (str): The user's password.

    Config:
        json_schema_extra (dict): Example of a login instance.
    """
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }
