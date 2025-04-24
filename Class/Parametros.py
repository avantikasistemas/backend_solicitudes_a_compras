from Utils.tools import Tools, CustomException
from Utils.querys import Querys

class Parametros:

    def __init__(self, db):
        self.db = db
        self.tools = Tools()
        self.querys = Querys(self.db)
        self.CORPORATIVA = 1
        self.ROL = 2
        self.POSICION = 3

    # Función para obtener los parametros iniciales
    def get_parametros(self):
        """ Api que realiza la consulta de los estados. """

        try:

            # Llamamos a la función de consultar get_nivel_formacion
            usuarios = self.querys.get_negociadores()

            # Retornamos la información.
            return self.tools.output(200, "Datos encontrados.", usuarios)

        except Exception as e:
            print(f"Error al obtener información de tercero: {e}")
            raise CustomException("Error al obtener información de tercero.")
