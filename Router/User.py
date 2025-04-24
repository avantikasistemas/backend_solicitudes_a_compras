from Utils.tools import Tools
from sqlalchemy.orm import Session
from fastapi import APIRouter, Request, Depends
from Class.User import User
from Schemas.Login.login import Login
from Utils.decorator import http_decorator
from Middleware.jwt_bearer import JWTBearer
from Config.db import get_db

tools = Tools()
user_router = APIRouter()

@user_router.post('/login', tags=["Auth"], response_model=dict)
@http_decorator
def login(request: Request, login: Login, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = User(db).login(data)
    return response
