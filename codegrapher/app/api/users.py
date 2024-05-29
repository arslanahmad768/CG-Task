from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from typing import Annotated
from ..database import database
from ..models.user import UserInDB, TokenData, User
import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

user_collection = database.get_collection("users_collection")

load_dotenv()

def user_helper(user) -> dict:
    """
    Helper function to transform a MongoDB user document into a dictionary.

    Args:
        user (dict): The user document.

    Returns:
        dict: A dictionary containing the user's details.
    """
    return {
        "id": str(user["_id"]),
        "fullname": user["fullname"],
        "email": user["email"],
        "city": user["city"],
        "disabled": user["disabled"],
    }
    

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta, optional): The token expiration time.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hash a plain password.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def get_user(db, email: str):
    """
    Retrieve a user from the database by email.

    Args:
        db (dict): The database.
        email (str): The user's email.

    Returns:
        UserInDB: The user data.
    """
    if email in db:
        user_dict = db[email]
        return UserInDB(**user_dict)

def decode_token(token: str):
    """
    Decode a JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        dict: The decoded token data.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=os.getenv("ALGORITHM"))
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Retrieve the current user based on the provided token.

    Args:
        token (str): The JWT token.

    Returns:
        UserInDB: The user data.

    Raises:
        HTTPException: If the token is invalid or the user cannot be validated.
    """

    print("GET current User-----")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        print("payload is---", payload)
        email: str = payload.get("sub")
        if email is None:
            print("Email is None")
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    print("Email is----", email)
    user = await user_collection.find_one({"email": token_data.email})
    print("User found----", user)
    if user is None:
        raise credentials_exception
    return User(**user)


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve the current active user.

    Args:
        current_user (User): The current user data.

    Returns:
        User: The current active user.

    Raises:
        HTTPException: If the user is inactive.
    """
    print("Latest current User", current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def login(user_data):
    """
    User login function to authenticate and generate a JWT token.

    Args:
        user_data (UserLoginSchema): The user login data.

    Returns:
        str: The JWT token.

    Raises:
        HTTPException: If the credentials are incorrect.
    """
    user = await user_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    access_token = create_access_token({"sub": user["email"]})
    return access_token

async def add_user(user_data: dict) -> dict:
    """
    Add a new user to the database.

    Args:
        user_data (dict): The user data.

    Returns:
        dict: The added user data.

    Raises:
        HTTPException: If the email is already registered.
    """
    user_exists = await user_collection.find_one({"email": user_data["email"]})
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_data["password"] = get_password_hash(user_data["password"])
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

async def retrieve_users():
    """
    Retrieve all users from the database.

    Returns:
        list: A list of all users.
    """
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users