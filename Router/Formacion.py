from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from Schemas.Formacion.guardar_formacion import GuardarFormacion
from Class.Formacion import Formacion
from Utils.decorator import http_decorator
from Config.db import get_db
from Middleware.jwt_bearer import JWTBearer

formacion_router = APIRouter()

@formacion_router.post('/guardar_formacion', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def guardar_formacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).guardar_formacion(data)
    return response

@formacion_router.post('/get_formaciones', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def get_formaciones(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).get_formaciones(data)
    return response

@formacion_router.post('/get_formacion_by_id', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def get_formacion_by_id(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).get_formacion_by_id(data)
    return response

@formacion_router.post('/actualizar_formacion', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def actualizar_formacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).actualizar_formacion(data)
    return response

@formacion_router.post('/guardar_personal_formacion', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def guardar_personal_formacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).guardar_personal_formacion(data)
    return response

@formacion_router.post('/obtener_personal_seleccionado_formacion', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def obtener_personal_seleccionado_formacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).obtener_personal_seleccionado_formacion(data)
    return response

@formacion_router.post('/actualizar_macroprocesos', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def actualizar_macroprocesos(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).actualizar_macroprocesos(data)
    return response

@formacion_router.post('/consultar_datos', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def consultar_datos(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).consultar_datos(data)
    return response

@formacion_router.post('/guardar_calificacion', tags=["Formacion"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def guardar_calificacion(request: Request, db: Session = Depends(get_db)):
    data = getattr(request.state, "json_data", {})
    response = Formacion(db).guardar_calificacion(data)
    return response
