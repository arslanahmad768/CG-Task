from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from ..api.users import add_user, login

from ..models.user import (
    ResponseModel,
    UserInDB,
    UserLoginSchema,
    Token
)

UserRouter = APIRouter()

@UserRouter.post("/", response_description="user data added into the database")
async def add_user_data(data: UserInDB = Body(...)):
    data = jsonable_encoder(data)
    print("User data----", data)
    new_user = await add_user(data)
    return ResponseModel(new_user, "user added successfully.")

def oauth2_to_user_login_schema(form_data: OAuth2PasswordRequestForm = Depends()):
    # Transform the form_data to match your UserLoginSchema
    user_data = UserLoginSchema(email=form_data.username, password=form_data.password)
    return user_data

@UserRouter.post("/token", response_description="User Login successfully")
async def user_login(formdata: UserLoginSchema = Depends(oauth2_to_user_login_schema)):
    print("User information----", formdata.email)
    access_token = await login(formdata)
    return Token(access_token=access_token, token_type="bearer")