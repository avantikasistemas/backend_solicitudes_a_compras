from Utils.tools import Tools, CustomException
from Utils.jwt_manager import create_token
from Utils.querys import Querys

class User:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()

        # Cargamos los usuarios admin desde la BD (tipo=1), VNIETO siempre hardcodeado
        try:
            admin_from_db = Querys(self.db).get_negociadores(tipo=1)
            admin_usuarios = [u["usuario"] for u in admin_from_db if u["usuario"] != 'VNIETO']
        except Exception:
            admin_usuarios = []

        # Cargamos coordinadores de solicitudes (tipo=1), VNIETO siempre hardcodeado
        try:
            coordinadores_from_db = Querys(self.db).get_solicitantes_tipo1()
            coordinadores_usuarios = [u["usuario"] for u in coordinadores_from_db if u["usuario"] != 'VNIETO']
        except Exception:
            coordinadores_usuarios = []

        self.querys = Querys(self.db)
        self.cuentas_validas = [
            'JAMARTINEZ', 'VNIETO', 'WOSPINO', 'ABEGAMBRE', 'JCARDENAS',
            'KGARCIA', 'CGUZMAN', 'JHERRERAM', 'DMEZA', 'CMUNIVE', 'AOLMOS1',
            'KORDOSGOIT', 'LBOROZCO', 'JPOROZCO', 'KRAMOS', 'KROMERO',
            'vvillalobo', 'HMARTINEZ', 'RODRIGUEZC', 'KMERCADO', 'MCASALINS',
            'MMIRANDA2', 'NFERNANDEZ', 'YORDONEZ2', 'PCARBONELL'
        ]
        # Usuarios administradores: VNIETO hardcodeado + los de tipo=1 en BD
        self.usuarios_admin = ['VNIETO'] + admin_usuarios
        # Coordinadores de solicitudes: VNIETO hardcodeado + tipo=1 en BD
        self.usuarios_solicitante_admin = ['VNIETO'] + coordinadores_usuarios

    # Función para loguear en el aplicativo
    def login(self, data):

        usuario = data["usuario"].upper()
        password = data["password"]

        # if usuario not in self.cuentas_validas:
        #     raise CustomException("Usuario no es valido para acceder.")

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

        # Verificar si el usuario es solicitante normal (tipo=2)
        es_solicitante, tipo_solicitante = self.querys.verificar_es_solicitante(usuario)
        if usuario in self.usuarios_solicitante_admin:
            data_user["es_solicitante_normal"] = False
        elif es_solicitante and tipo_solicitante == 2:
            data_user["es_solicitante_normal"] = True
        else:
            data_user["es_solicitante_normal"] = False

        token = create_token(
            {
                "nombre": data_user["nombre"], 
                "cedula": data_user["cedula"]
            }
        )
        data_user["token"] = token
        return self.tools.output(200, "Acceso exitoso.", data_user)
