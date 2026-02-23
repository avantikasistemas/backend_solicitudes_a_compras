from Utils.tools import Tools, CustomException
from Utils.jwt_manager import create_token
from Utils.querys import Querys

class User:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.cuentas_validas = [
            'JAMARTINEZ', 'VNIETO', 'WOSPINO', 'ABEGAMBRE', 'JCARDENAS',
            'KGARCIA', 'CGUZMAN', 'JHERRERAM', 'DMEZA', 'CMUNIVE', 'AOLMOS1',
            'KORDOSGOIT', 'LBOROZCO', 'JPOROZCO', 'KRAMOS', 'KROMERO',
            'vvillalobo', 'HMARTINEZ', 'RODRIGUEZC', 'KMERCADO', 'MCASALINS',
            'MMIRANDA2', 'NFERNANDEZ', 'YORDONEZ2', 'PCARBONELL'
        ]
        # Usuarios administradores que pueden ver todas las solicitudes
        self.usuarios_admin = ['PCARBONELL', 'RODRIGUEZC', 'VNIETO']

    # Función para loguear en el aplicativo
    def login(self, data):

        usuario = data["usuario"].upper()
        password = data["password"]

        if usuario not in self.cuentas_validas:
            raise CustomException("Usuario no es valido para acceder.")

        data_user = self.querys.get_usuario(usuario, password)

        # Verificar si el usuario es negociador
        es_negociador = self.querys.verificar_es_negociador(usuario)
        
        # Determinar el rol del usuario
        if usuario in self.usuarios_admin:
            # Usuarios admin pueden ver todas las solicitudes
            data_user["rol"] = "admin"
            data_user["es_negociador"] = False
        elif es_negociador:
            # Usuario es negociador, solo ve sus solicitudes
            data_user["rol"] = "negociador"
            data_user["es_negociador"] = True
        else:
            # Usuario normal, puede ver todas las solicitudes
            data_user["rol"] = "usuario"
            data_user["es_negociador"] = False

        token = create_token(
            {
                "nombre": data_user["nombre"], 
                "cedula": data_user["cedula"]
            }
        )
        data_user["token"] = token
        return self.tools.output(200, "Acceso exitoso.", data_user)
