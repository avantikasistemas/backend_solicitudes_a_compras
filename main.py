from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Config.db import BASE, engine
from Middleware.get_json import JSONMiddleware
# from Router.User import user_router
from Router.Parametros import parametros_router
# from Router.Formacion import formacion_router

app = FastAPI()
app.title = "Avantika Solicitud Cotizaciones a Compras"
app.version = "0.0.1"

app.add_middleware(JSONMiddleware)
app.add_middleware(
    CORSMiddleware,allow_origins=["*"],  # Permitir todos los orígenes; para producción, especifica los orígenes permitidos.
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos; puedes especificar los métodos permitidos.
    allow_headers=["*"],  # Permitir todos los encabezados; puedes especificar los encabezados permitidos.
)
app.include_router(parametros_router)
# app.include_router(user_router)
# app.include_router(formacion_router)

BASE.metadata.create_all(bind=engine)
