from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Class.Solicitud import Solicitud
from Utils.decorator import http_decorator
from Config.db import get_db
from Middleware.jwt_bearer import JWTBearer

solicitud_router = APIRouter()

@solicitud_router.post('/guardar_solicitud', tags=["Solicitud"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def guardar_solicitud(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Solicitud(db).guardar_solicitud(data)
    return response

@solicitud_router.post('/mostrar_solicitudes', tags=["Solicitud"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def mostrar_solicitudes(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Solicitud(db).mostrar_solicitudes(data)
    return response

@solicitud_router.post('/actualizar_negociador', tags=["Solicitud"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def actualizar_negociador(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Solicitud(db).actualizar_negociador(data)
    return response

@solicitud_router.post('/actualizar_estado', tags=["Solicitud"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def actualizar_estado(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Solicitud(db).actualizar_estado(data)
    return response
