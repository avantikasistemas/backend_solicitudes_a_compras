from Utils.tools import Tools, CustomException
from Utils.jwt_manager import create_token
from Utils.querys import Querys

class User:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.cuentas_validas = [
            'AGAMEZ', 'PPAJARO', 'JAMARTINEZ', 'VNIETO', 'LLEDESMA'
        ]

    # Función para loguear en el aplicativo
    def login(self, data):

        usuario = data["usuario"].upper()
        password = data["password"]

        if usuario not in self.cuentas_validas:
            raise CustomException("Usuario no es valido para acceder.")

        data_user = self.querys.get_usuario(usuario, password)

        token = create_token(
            {
                "nombre": data_user["nombre"], 
                "cedula": data_user["cedula"]
            }
        )
        data_user["token"] = token
        return self.tools.output(200, "Acceso exitoso.", data_user)
