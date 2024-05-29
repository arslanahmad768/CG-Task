from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from ..api.users import add_user, login

from ..models.user import (
    UserInDB,
    UserLoginSchema,
    Token
)
from ..helpers import ResponseModel

UserRouter = APIRouter()

@UserRouter.post("/", response_description="User data added into the database")
async def add_user_data(data: UserInDB = Body(...)):
    """
    Add a new user to the database.

    Args:
        data (UserInDB): The user data to add to the database.

    Returns:
        ResponseModel: A response model containing the new user data and a success message.
    """
    data = jsonable_encoder(data)
    new_user = await add_user(data)
    return ResponseModel(new_user, "User added successfully.")

def oauth2_to_user_login_schema(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Convert OAuth2 form data to UserLoginSchema.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data from the OAuth2 request.

    Returns:
        UserLoginSchema: The user login schema with email and password.
    """
    user_data = UserLoginSchema(email=form_data.username, password=form_data.password)
    return user_data

@UserRouter.post("/token", response_description="User logged in successfully")
async def user_login(formdata: UserLoginSchema = Depends(oauth2_to_user_login_schema)):
    """
    User login endpoint.

    Args:
        formdata (UserLoginSchema): The user login data.

    Returns:
        Token: A token model containing the access token and token type.
    """
    access_token = await login(formdata)
    return Token(access_token=access_token, token_type="bearer")

