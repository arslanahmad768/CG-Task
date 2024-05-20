from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from ..api.users import add_user, login

from ..models.user import (
    ResponseModel,
    UserSchema,
    UserLoginSchema
)

UserRouter = APIRouter()

@UserRouter.post("/", response_description="user data added into the database")
async def add_user_data(user: UserSchema = Body(...)):
    user = jsonable_encoder(user)
    new_user = await add_user(user)
    return ResponseModel(new_user, "user added successfully.")

@UserRouter.post("/login", response_description="User Login successfully")
async def user_login(user: UserLoginSchema = Body(...)):
    user = jsonable_encoder(user)
    user = await login(user)
    return ResponseModel(user, "User Login successfully")